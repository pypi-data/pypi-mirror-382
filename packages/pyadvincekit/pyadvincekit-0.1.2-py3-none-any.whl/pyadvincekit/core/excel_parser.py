#!/usr/bin/env python3
"""
Excel数据库设计解析器

专门用于解析特定格式的Excel数据库设计文件
"""

import os
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import pandas as pd

from pyadvincekit.logging import get_logger
from pyadvincekit.core.excel_generator import (
    ColumnType, ConstraintType, ColumnConstraint, TableColumn, 
    TableDefinition, DatabaseDesign, TableIndex
)

logger = get_logger(__name__)


class DatabaseDesignParser:
    """数据库设计解析器"""
    
    def __init__(self, add_standard_fields: bool = True):
        self.add_standard_fields = add_standard_fields
        self.supported_types = {
            # 整数类型
            "int": ColumnType.INTEGER,
            "integer": ColumnType.INTEGER,
            "bigint": ColumnType.BIGINT,
            "smallint": ColumnType.SMALLINT,
            "tinyint": ColumnType.TINYINT,
            "long": ColumnType.BIGINT,  # Long类型映射到BIGINT
            
            # 浮点类型
            "float": ColumnType.FLOAT,
            "double": ColumnType.DOUBLE,
            "decimal": ColumnType.DECIMAL,
            "numeric": ColumnType.DECIMAL,
            
            # 字符串类型
            "varchar": ColumnType.VARCHAR,
            "char": ColumnType.CHAR,
            "text": ColumnType.TEXT,
            "longtext": ColumnType.LONGTEXT,
            "string": ColumnType.VARCHAR,
            "str": ColumnType.VARCHAR,
            
            # 日期时间类型
            "date": ColumnType.DATE,
            "datetime": ColumnType.DATETIME,
            "timestamp": ColumnType.TIMESTAMP,
            "time": ColumnType.TIME,
            
            # 布尔类型
            "boolean": ColumnType.BOOLEAN,
            "bool": ColumnType.BOOLEAN,
            
            # JSON类型
            "json": ColumnType.JSON,
            
            # 二进制类型
            "blob": ColumnType.BLOB,
            "longblob": ColumnType.LONGBLOB,
        }
    
    def parse_excel_file(self, file_path: str) -> DatabaseDesign:
        """解析Excel文件"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        logger.info(f"Parsing Excel file: {file_path}")
        
        # 读取Excel文件
        if file_path.lower().endswith('.xls'):
            excel_data = pd.read_excel(file_path, sheet_name=None, engine='xlrd')
        else:
            excel_data = pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
        
        # 解析数据库设计
        design = DatabaseDesign(name="Generated Database")
        
        # 解析每个工作表
        for sheet_name, sheet_data in excel_data.items():
            logger.info(f"Processing sheet: {sheet_name}")
            table = self._parse_table(sheet_name, sheet_data)
            if table:
                design.tables.append(table)
        
        logger.info(f"Parsed {len(design.tables)} tables from Excel file")
        return design
    
    def _create_standard_columns(self) -> List[TableColumn]:
        """创建标准字段：id, created_at, updated_at"""
        standard_columns = []
        
        # 1. 主键 ID 字段
        id_column = TableColumn(
            name="id",
            type=ColumnType.VARCHAR,
            length=36,  # UUID 长度
            nullable=False,
            comment="主键ID",
            default_value="(UUID())",  # MySQL 函数格式
            constraints=[
                ColumnConstraint(
                    type=ConstraintType.PRIMARY_KEY
                )
            ]
        )
        standard_columns.append(id_column)
        
        # 2. 创建时间字段
        created_at_column = TableColumn(
            name="created_at",
            type=ColumnType.DATETIME,
            nullable=False,
            comment="创建时间",
            default_value="CURRENT_TIMESTAMP"
        )
        standard_columns.append(created_at_column)
        
        # 3. 更新时间字段  
        # 注意：ON UPDATE 逻辑将在 SQL 生成器中处理
        updated_at_column = TableColumn(
            name="updated_at",
            type=ColumnType.DATETIME,
            nullable=False,
            comment="更新时间", 
            default_value="CURRENT_TIMESTAMP"
        )
        # 使用特殊标记来表示需要 ON UPDATE
        updated_at_column.comment += " [AUTO_UPDATE]"
        standard_columns.append(updated_at_column)
        
        logger.info("Added standard columns: id, created_at, updated_at")
        return standard_columns
    
    def _parse_table(self, sheet_name: str, data: pd.DataFrame) -> Optional[TableDefinition]:
        """解析表定义"""
        if data.empty or len(data) < 5:
            logger.warning(f"Sheet {sheet_name} has insufficient data, skipping")
            return None
        
        # 🔥 新增校验：检查A0和A1单元格内容是否符合表格式
        try:
            # 检查A0单元格是否为"表名"
            a0_value = str(data.iloc[0, 0]).strip() if not pd.isna(data.iloc[0, 0]) else ""
            # 检查A1单元格是否为"表描述"  
            a1_value = str(data.iloc[1, 0]).strip() if not pd.isna(data.iloc[1, 0]) else ""
            
            if a0_value != "表描述" or a1_value != "表空间":
                logger.info(f"Sheet {sheet_name} is not a table definition (A0='{a0_value}', A1='{a1_value}'), skipping")
                return None
                
            logger.info(f"Sheet {sheet_name} passed table validation (A0='{a0_value}', A1='{a1_value}')")
            
        except Exception as e:
            logger.warning(f"Error validating sheet {sheet_name}: {e}, skipping")
            return None
        
        # 获取表信息（前4行）
        table_info = self._extract_table_info(data)
        table_name = table_info.get('name', sheet_name)
        
        # 获取列信息（从第5行开始）
        columns = self._extract_columns(data)
        
        if not columns:
            logger.warning(f"Sheet {sheet_name} has no valid columns, skipping")
            return None
        
        table = TableDefinition(
            name=table_name,
            comment=table_info.get('description', ''),
            engine="InnoDB",
            charset="utf8mb4",
            collate="utf8mb4_unicode_ci"
        )
        
        # 🔥 根据配置决定是否自动添加标准字段
        if self.add_standard_fields:
            standard_columns = self._create_standard_columns()
            for std_column in standard_columns:
                table.columns.append(std_column)
        
        # 添加用户定义的列
        for column in columns:
            table.columns.append(column)
        
        # 添加索引
        indexes = self._extract_indexes(data, table_name)
        for index in indexes:
            table_index = TableIndex(
                name=index["name"],
                columns=index["columns"],
                unique=index["unique"],
                type=index["type"]
            )
            table.indexes.append(table_index)
        
        logger.info(f"Table {table.name}: {len(table.columns)} columns, {len(table.indexes)} indexes")
        return table
    
    def _extract_table_info(self, data: pd.DataFrame) -> dict:
        """提取表信息"""
        info = {}
        
        # 根据用户说明：
        # B0是表名，B1是表描述，B2是表空间，B3是索引空间
        # 在pandas中，B列是索引1（0-based）
        
        if len(data) >= 1 and len(data.columns) > 1:
            # B0 - 表名
            info['name'] = str(data.columns[1]).strip()
        
        if len(data) >= 2 and len(data.columns) > 1:
            # B1 - 表描述
            if pd.notna(data.iloc[0, 1]):
                info['description'] = str(data.iloc[0, 1]).strip()
        
        if len(data) >= 3 and len(data.columns) > 1:
            # B2 - 表空间
            if pd.notna(data.iloc[1, 1]):
                info['tablespace'] = str(data.iloc[1, 1]).strip()
        
        if len(data) >= 4 and len(data.columns) > 1:
            # B3 - 索引空间
            if pd.notna(data.iloc[2, 1]):
                info['indexspace'] = str(data.iloc[2, 1]).strip()
        
        logger.info(f"Table info: {info}")
        return info
    
    def _extract_columns(self, data: pd.DataFrame) -> List[TableColumn]:
        """提取列定义"""
        columns = []
        
        # 从第5行开始是列定义（索引4）
        start_row = 3
        if len(data) <= start_row:
            return columns
        
        # 获取列标题行
        header_row = data.iloc[start_row]
        column_headers = [str(header).strip() for header in header_row if pd.notna(header)]
        
        logger.info(f"Column headers: {column_headers}")
        
        # 解析每一列
        for i in range(start_row + 1, len(data)):
            row = data.iloc[i]
            if len(row) < 3:  # 至少需要列名、类型、长度
                continue
            
            column = self._parse_column(row, column_headers)
            if column:
                columns.append(column)
        
        return columns
    
    def _parse_column(self, row: pd.Series, headers: List[str]) -> Optional[TableColumn]:
        """解析列定义"""
        if len(row) < 3:
            return None
        
        # 获取基本信息
        name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        type_str = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
        length_str = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
        
        if not name or not type_str:
            return None
        
        # 解析长度
        length = None
        if length_str and length_str.isdigit():
            length = int(length_str)
        
        # 确定列类型
        column_type = self._get_column_type(type_str)
        if not column_type:
            logger.warning(f"Unknown column type: {type_str}")
            return None
        
        # 创建列对象
        column = TableColumn(
            name=name,
            type=column_type,
            length=length,
            nullable=True,  # 默认可为空
            comment=""
        )
        
        # 解析其他属性
        if len(row) > 3:
            # 空值列
            null_str = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else ""
            if null_str and "否" in null_str:
                column.nullable = False
        
        if len(row) > 4:
            # 缺省值
            default_str = str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) else ""
            if default_str and default_str != "":
                column.default_value = default_str
        
        if len(row) > 5:
            # 中文名称作为注释
            chinese_name = str(row.iloc[5]).strip() if pd.notna(row.iloc[5]) else ""
            if chinese_name:
                column.comment = chinese_name
        
        # 解析约束（从索引列）
        self._parse_column_constraints(column, row, headers)
        
        return column
    
    def _parse_column_constraints(self, column: TableColumn, row: pd.Series, headers: List[str]):
        """解析列约束"""
        # 查找唯一索引列
        for i, header in enumerate(headers):
            if "UIDX" in header or "唯一索引" in header:
                if i < len(row) and pd.notna(row.iloc[i]):
                    value = str(row.iloc[i]).strip()
                    if value and "Y" in value.upper():
                        column.constraints.append(ColumnConstraint(ConstraintType.UNIQUE))
                        break
        
        # 查找主键（通常第一个唯一索引是主键）
        if column.constraints and column.constraints[0].type == ConstraintType.UNIQUE:
            # 将第一个唯一约束设为主键
            column.constraints[0].type = ConstraintType.PRIMARY_KEY
    
    def _extract_indexes(self, data: pd.DataFrame, table_name: str) -> List[Dict[str, Any]]:
        """提取索引定义"""
        indexes = []
        
        if len(data) < 5:
            return indexes
        
        # 第5行（索引4）是列标题行，从H列开始是索引信息
        # H列是索引7（0-based）
        header_row = data.iloc[3]
        
        # 查找索引列
        index_columns = []
        for i, header in enumerate(header_row):
            if pd.notna(header):
                header_str = str(header).strip()
                if "UIDX" in header_str or "IDX" in header_str:
                    index_columns.append((i, header_str))
        
        logger.info(f"Found index columns: {index_columns}")
        
        # 按索引名称收集列
        index_columns_map = {}
        
        # 解析每一行的索引信息
        for row_idx in range(3, len(data)):
            row = data.iloc[row_idx]
            if len(row) < 3:  # 至少需要列名
                continue
            
            column_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            if not column_name:
                continue
            
            # 检查每个索引列
            for col_idx, index_name in index_columns:
                if col_idx < len(row) and pd.notna(row.iloc[col_idx]):
                    value = str(row.iloc[col_idx]).strip()
                    if value and "Y" in value.upper():
                        # 收集到索引映射中
                        if index_name not in index_columns_map:
                            index_columns_map[index_name] = []
                        index_columns_map[index_name].append(column_name)
        
        # 创建索引
        for index_name, columns in index_columns_map.items():
            if columns:
                if "UIDX" in index_name:
                    # 唯一索引
                    index = self._create_index(index_name, columns, True, table_name)
                else:
                    # 非唯一索引
                    index = self._create_index(index_name, columns, False, table_name)
                
                if index:
                    indexes.append(index)
        
        logger.info(f"Created {len(indexes)} indexes")
        return indexes
    
    def _create_index(self, index_name: str, columns: List[str], unique: bool, table_name: str) -> Optional[Dict[str, Any]]:
        """创建索引对象"""
        if not columns:
            return None
        
        # 生成索引名称
        full_index_name = f"{index_name}_{table_name}"
        
        return {
            "name": full_index_name,
            "columns": columns,
            "unique": unique,
            "type": "BTREE"
        }
    
    def _get_column_type(self, type_str: str) -> Optional[ColumnType]:
        """获取列类型"""
        # 清理类型字符串
        type_str = re.sub(r'[^a-zA-Z0-9]', '', type_str.lower())
        
        return self.supported_types.get(type_str)


# 便捷函数
def parse_database_design_excel(file_path: str) -> DatabaseDesign:
    """解析数据库设计Excel文件的便捷函数"""
    parser = DatabaseDesignParser()
    return parser.parse_excel_file(file_path)

