#!/usr/bin/env python3
"""
Excel数据库设计自动生成器

从Excel文件自动生成SQL、ORM和Pydantic对象
"""

import os
import re
from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime

from pyadvincekit.logging import get_logger

if TYPE_CHECKING:
    import pandas as pd

logger = get_logger(__name__)


class ColumnType(Enum):
    """数据库列类型"""
    # 整数类型
    INTEGER = "INTEGER"
    BIGINT = "BIGINT"
    SMALLINT = "SMALLINT"
    TINYINT = "TINYINT"
    
    # 浮点类型
    FLOAT = "FLOAT"
    DOUBLE = "DOUBLE"
    DECIMAL = "DECIMAL"
    
    # 字符串类型
    VARCHAR = "VARCHAR"
    CHAR = "CHAR"
    TEXT = "TEXT"
    LONGTEXT = "LONGTEXT"
    
    # 日期时间类型
    DATE = "DATE"
    DATETIME = "DATETIME"
    TIMESTAMP = "TIMESTAMP"
    TIME = "TIME"
    
    # 布尔类型
    BOOLEAN = "BOOLEAN"
    
    # JSON类型
    JSON = "JSON"
    
    # 二进制类型
    BLOB = "BLOB"
    LONGBLOB = "LONGBLOB"


class ConstraintType(Enum):
    """约束类型"""
    PRIMARY_KEY = "PRIMARY KEY"
    FOREIGN_KEY = "FOREIGN KEY"
    UNIQUE = "UNIQUE"
    NOT_NULL = "NOT NULL"
    DEFAULT = "DEFAULT"
    CHECK = "CHECK"
    INDEX = "INDEX"


@dataclass
class ColumnConstraint:
    """列约束"""
    type: ConstraintType
    value: Optional[str] = None
    reference_table: Optional[str] = None
    reference_column: Optional[str] = None


@dataclass
class TableColumn:
    """表列定义"""
    name: str
    type: ColumnType
    length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    nullable: bool = True
    default_value: Optional[str] = None
    comment: str = ""
    constraints: List[ColumnConstraint] = field(default_factory=list)
    
    def get_sql_type(self) -> str:
        """获取SQL类型字符串"""
        type_str = self.type.value
        
        if self.type in [ColumnType.VARCHAR, ColumnType.CHAR] and self.length:
            type_str += f"({self.length})"
        elif self.type == ColumnType.DECIMAL and self.precision and self.scale:
            type_str += f"({self.precision},{self.scale})"
        elif self.type == ColumnType.DECIMAL and self.precision:
            type_str += f"({self.precision})"
        
        return type_str


@dataclass
class TableIndex:
    """表索引"""
    name: str
    columns: List[str]
    unique: bool = False
    type: str = "BTREE"


@dataclass
class TableDefinition:
    """表定义"""
    name: str
    comment: str = ""
    columns: List[TableColumn] = field(default_factory=list)
    indexes: List[TableIndex] = field(default_factory=list)
    engine: str = "InnoDB"
    charset: str = "utf8mb4"
    collate: str = "utf8mb4_unicode_ci"


@dataclass
class DatabaseDesign:
    """数据库设计"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    tables: List[TableDefinition] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class ExcelParser:
    """Excel解析器"""
    
    def __init__(self):
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
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for Excel parsing. Install with: pip install pandas openpyxl")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        logger.info(f"Parsing Excel file: {file_path}")
        
        # 读取Excel文件
        # 根据文件扩展名选择引擎
        if file_path.lower().endswith('.xls'):
            # .xls文件使用xlrd引擎
            try:
                excel_data = pd.read_excel(file_path, sheet_name=None, engine='xlrd')
            except ImportError:
                raise ImportError("xlrd is required for .xls files. Install with: pip install xlrd")
        else:
            # .xlsx文件使用openpyxl引擎
            try:
                excel_data = pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
            except ImportError:
                raise ImportError("openpyxl is required for .xlsx files. Install with: pip install openpyxl")
        
        # 解析数据库设计
        design = DatabaseDesign(name="Generated Database")
        
        # 解析每个工作表作为表定义
        for sheet_name, sheet_data in excel_data.items():
            if sheet_name.lower() in ['_metadata', 'metadata', 'info']:
                # 解析元数据
                self._parse_metadata(sheet_data, design)
            else:
                # 解析表定义
                table = self._parse_table(sheet_name, sheet_data)
                if table:
                    design.tables.append(table)
        
        logger.info(f"Parsed {len(design.tables)} tables from Excel file")
        return design
    
    def _parse_metadata(self, data: "pd.DataFrame", design: DatabaseDesign):
        """解析元数据"""
        for _, row in data.iterrows():
            key = str(row.iloc[0]).lower() if len(row) > 0 else ""
            value = str(row.iloc[1]) if len(row) > 1 else ""
            
            if key == "name":
                design.name = value
            elif key == "version":
                design.version = value
            elif key == "description":
                design.description = value
    
    def _parse_table(self, table_name: str, data: "pd.DataFrame") -> Optional[TableDefinition]:
        """解析表定义"""
        if data.empty:
            return None
        
        # 预期的列结构：列名, 类型, 长度, 是否为空, 默认值, 注释, 约束
        expected_columns = ["列名", "类型", "长度", "是否为空", "默认值", "注释", "约束"]
        
        # 检查列名
        if len(data.columns) < 2:
            logger.warning(f"Table {table_name} has insufficient columns")
            return None
        
        table = TableDefinition(name=table_name)
        
        for _, row in data.iterrows():
            try:
                column = self._parse_column(row)
                if column:
                    table.columns.append(column)
            except Exception as e:
                logger.warning(f"Failed to parse column in table {table_name}: {e}")
                continue
        
        return table if table.columns else None
    
    def _parse_column(self, row: "pd.Series") -> Optional[TableColumn]:
        """解析列定义"""
        if len(row) < 2:
            return None
        
        # 获取列信息
        name = str(row.iloc[0]).strip()
        type_str = str(row.iloc[1]).strip().lower()
        length = None
        nullable = True
        default_value = None
        comment = ""
        constraints = []
        
        # 解析长度
        if len(row) > 2 and pd.notna(row.iloc[2]):
            try:
                length = int(row.iloc[2])
            except (ValueError, TypeError):
                pass
        
        # 解析是否为空
        if len(row) > 3 and pd.notna(row.iloc[3]):
            nullable_str = str(row.iloc[3]).strip().lower()
            nullable = nullable_str not in ["no", "false", "0", "否", "不可为空"]
        
        # 解析默认值
        if len(row) > 4 and pd.notna(row.iloc[4]):
            default_value = str(row.iloc[4]).strip()
            if default_value.lower() in ["null", "none", ""]:
                default_value = None
        
        # 解析注释
        if len(row) > 5 and pd.notna(row.iloc[5]):
            comment = str(row.iloc[5]).strip()
        
        # 解析约束
        if len(row) > 6 and pd.notna(row.iloc[6]):
            constraint_str = str(row.iloc[6]).strip()
            constraints = self._parse_constraints(constraint_str)
        
        # 确定列类型
        column_type = self._get_column_type(type_str)
        if not column_type:
            logger.warning(f"Unknown column type: {type_str}")
            return None
        
        return TableColumn(
            name=name,
            type=column_type,
            length=length,
            nullable=nullable,
            default_value=default_value,
            comment=comment,
            constraints=constraints
        )
    
    def _get_column_type(self, type_str: str) -> Optional[ColumnType]:
        """获取列类型"""
        # 清理类型字符串
        type_str = re.sub(r'[^a-zA-Z0-9]', '', type_str.lower())
        
        return self.supported_types.get(type_str)
    
    def _parse_constraints(self, constraint_str: str) -> List[ColumnConstraint]:
        """解析约束"""
        constraints = []
        
        if not constraint_str:
            return constraints
        
        # 分割约束
        constraint_parts = [part.strip() for part in constraint_str.split(',')]
        
        for part in constraint_parts:
            part = part.upper()
            
            if "PRIMARY KEY" in part or "主键" in part:
                constraints.append(ColumnConstraint(ConstraintType.PRIMARY_KEY))
            elif "UNIQUE" in part or "唯一" in part:
                constraints.append(ColumnConstraint(ConstraintType.UNIQUE))
            elif "NOT NULL" in part or "非空" in part:
                constraints.append(ColumnConstraint(ConstraintType.NOT_NULL))
            elif "FOREIGN KEY" in part or "外键" in part:
                # 解析外键引用
                ref_match = re.search(r'REFERENCES\s+(\w+)\.(\w+)', part)
                if ref_match:
                    constraints.append(ColumnConstraint(
                        ConstraintType.FOREIGN_KEY,
                        reference_table=ref_match.group(1),
                        reference_column=ref_match.group(2)
                    ))
                else:
                    # 如果没有找到具体的引用，仍然添加外键约束
                    constraints.append(ColumnConstraint(ConstraintType.FOREIGN_KEY))
            elif "INDEX" in part or "索引" in part:
                constraints.append(ColumnConstraint(ConstraintType.INDEX))
        
        return constraints


class SQLGenerator:
    """SQL生成器"""
    
    def __init__(self):
        self.dialect = "mysql"  # 默认MySQL
    
    def generate_create_database_sql(self, design: DatabaseDesign) -> str:
        """生成创建数据库的SQL"""
        sql = f"""-- 创建数据库
CREATE DATABASE IF NOT EXISTS `{design.name}` 
DEFAULT CHARACTER SET utf8mb4 
DEFAULT COLLATE utf8mb4_unicode_ci;

USE `{design.name}`;

"""
        return sql
    
    def generate_create_table_sql(self, table: TableDefinition) -> str:
        """生成创建表的SQL"""
        sql_lines = [f"-- 创建表: {table.name}"]
        if table.comment:
            sql_lines.append(f"-- {table.comment}")
        
        sql_lines.append(f"CREATE TABLE `{table.name}` (")
        
        # 生成列定义
        column_definitions = []
        primary_keys = []
        
        for column in table.columns:
            col_def = self._generate_column_definition(column)
            column_definitions.append(f"  {col_def}")
            
            # 收集主键
            for constraint in column.constraints:
                if constraint.type == ConstraintType.PRIMARY_KEY:
                    primary_keys.append(column.name)
        
        # 添加主键约束
        if primary_keys:
            column_definitions.append(f"  PRIMARY KEY (`{'`, `'.join(primary_keys)}`)")
        
        # 添加外键约束
        for column in table.columns:
            for constraint in column.constraints:
                if constraint.type == ConstraintType.FOREIGN_KEY:
                    fk_name = f"fk_{table.name}_{column.name}"
                    fk_def = f"  CONSTRAINT `{fk_name}` FOREIGN KEY (`{column.name}`) REFERENCES `{constraint.reference_table}` (`{constraint.reference_column}`)"
                    column_definitions.append(fk_def)
        
        sql_lines.append(",\n".join(column_definitions))
        sql_lines.append(f") ENGINE={table.engine} DEFAULT CHARSET={table.charset} COLLATE={table.collate};")
        
        # 添加索引
        for index in table.indexes:
            unique_keyword = "UNIQUE " if index.unique else ""
            sql_lines.append(f"CREATE {unique_keyword}INDEX `{index.name}` ON `{table.name}` (`{'`, `'.join(index.columns)}`);")
        
        return "\n".join(sql_lines) + "\n"
    
    def _generate_column_definition(self, column: TableColumn) -> str:
        """生成列定义"""
        parts = [f"`{column.name}`", column.get_sql_type()]
        
        # 添加NOT NULL约束
        if not column.nullable:
            parts.append("NOT NULL")
        
        # 添加默认值
        if column.default_value is not None:
            if column.default_value.upper() in ["CURRENT_TIMESTAMP", "NOW()"]:
                parts.append(f"DEFAULT {column.default_value}")
            else:
                # 智能处理默认值，避免重复引号
                default_val = column.default_value.strip()
                
                # 如果已经被引号包围，直接使用
                if (default_val.startswith("'") and default_val.endswith("'")) or \
                   (default_val.startswith('"') and default_val.endswith('"')):
                    # 移除外层引号，然后添加标准的单引号
                    inner_value = default_val[1:-1]
                    parts.append(f"DEFAULT '{inner_value}'")
                elif self._is_numeric_value(default_val):
                    # 数字不需要引号
                    parts.append(f"DEFAULT {default_val}")
                else:
                    # 字符串需要单引号
                    parts.append(f"DEFAULT '{default_val}'")
        
        # 🔥 检查是否需要 ON UPDATE（通过注释中的特殊标记）
        if column.comment and "[AUTO_UPDATE]" in column.comment:
            parts.append("ON UPDATE CURRENT_TIMESTAMP")
        
        # 添加注释（移除特殊标记）
        if column.comment:
            clean_comment = column.comment.replace(" [AUTO_UPDATE]", "")
            parts.append(f"COMMENT '{clean_comment}'")
        
        return " ".join(parts)
    
    def _is_numeric_value(self, value: str) -> bool:
        """检查值是否为数字（整数或小数）"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _clean_default_value(self, value: str) -> str:
        """清理默认值，移除多余的引号"""
        if not value:
            return value
            
        value = value.strip()
        
        # 如果被双引号包围，移除外层引号
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        
        # 如果被单引号包围，移除外层引号
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]
        
        return value
    
    def generate_all_sql(self, design: DatabaseDesign) -> str:
        """生成所有SQL"""
        sql_parts = [
            self.generate_create_database_sql(design),
            ""
        ]
        
        for table in design.tables:
            sql_parts.append(self.generate_create_table_sql(table))
            sql_parts.append("")
        
        return "\n".join(sql_parts)


class ORMGenerator:
    """ORM生成器"""
    
    def generate_model(self, table: TableDefinition) -> str:
        """生成SQLAlchemy模型（使用PyAdvanceKit封装的字段函数）"""
        imports = [
            "from typing import Optional",
            "from datetime import datetime, date, time",
            "from decimal import Decimal",
            "from sqlalchemy.orm import Mapped"
        ]
        
        # 如果有索引，需要导入Index
        if table.indexes:
            imports.append("from sqlalchemy import Index")
        
        imports.extend([
            "from pyadvincekit import (",
            "    BaseModel,",
            "    # 字段创建函数",
            "    create_required_string_column, create_optional_string_column, create_text_column,",
            "    create_integer_column, create_bigint_column, create_float_column,",
            "    create_boolean_column, create_datetime_column, create_date_column,",
            "    create_time_column, create_decimal_column, create_json_column,",
            "    create_status_column, create_version_column, create_foreign_key_column",
            ")"
        ])
        
        model_lines = [
            f"class {self._to_pascal_case(table.name)}(BaseModel):",
            f'    """{table.comment or f"{table.name} model"}"""',
            f'    __tablename__ = "{table.name}"',
            ""
        ]
        
        # 生成列定义（跳过标准字段，因为BaseModel已包含）
        standard_fields = {"id", "created_at", "updated_at"}
        for column in table.columns:
            if column.name not in standard_fields:
                model_lines.append(self._generate_pyadvincekit_column(column))
        
        # 🔥 生成索引定义
        if table.indexes:
            model_lines.append("")
            model_lines.append("    # 索引定义")
            index_definitions = []
            for index in table.indexes:
                index_def = self._generate_single_index_definition(index)
                index_definitions.append(index_def)
            
            # 将所有索引放在一个 __table_args__ 中
            if len(index_definitions) == 1:
                model_lines.append(f"    __table_args__ = ({index_definitions[0]},)")
            else:
                model_lines.append("    __table_args__ = (")
                for i, index_def in enumerate(index_definitions):
                    if i == len(index_definitions) - 1:
                        model_lines.append(f"        {index_def}")
                    else:
                        model_lines.append(f"        {index_def},")
                model_lines.append("    )")
        
        return "\n".join(imports + [""] + model_lines)
    
    def _generate_single_index_definition(self, index: TableIndex) -> str:
        """生成单个SQLAlchemy索引定义"""
        # 构建列引用列表
        column_refs = []
        for col_name in index.columns:
            column_refs.append(f"'{col_name}'")
        
        # 构建索引定义
        unique_param = ", unique=True" if index.unique else ""
        columns_str = ", ".join(column_refs)
        
        return f"Index('{index.name}', {columns_str}{unique_param})"
    
    def _generate_pyadvincekit_column(self, column: TableColumn) -> str:
        """生成使用PyAdvanceKit封装函数的列定义"""
        # 确定Python类型注解
        python_type = self._get_python_type_annotation(column)
        
        # 确定字段创建函数
        field_function = self._get_field_creation_function(column)
        
        # 构建字段定义
        return f"    {column.name}: {python_type} = {field_function}"
    
    def _get_python_type_annotation(self, column: TableColumn) -> str:
        """获取Python类型注解（包含Mapped包装）"""
        base_type = self._get_base_python_type(column.type)
        
        # 检查是否可为空
        if column.nullable and not self._has_not_null_constraint(column):
            return f"Mapped[Optional[{base_type}]]"
        else:
            return f"Mapped[{base_type}]"
    
    def _get_base_python_type(self, column_type: ColumnType) -> str:
        """获取基础Python类型"""
        type_mapping = {
            ColumnType.INTEGER: "int",
            ColumnType.BIGINT: "int", 
            ColumnType.SMALLINT: "int",
            ColumnType.TINYINT: "int",
            ColumnType.FLOAT: "float",
            ColumnType.DOUBLE: "float",
            ColumnType.DECIMAL: "Decimal",
            ColumnType.VARCHAR: "str",
            ColumnType.CHAR: "str", 
            ColumnType.TEXT: "str",
            ColumnType.LONGTEXT: "str",
            ColumnType.DATE: "date",
            ColumnType.DATETIME: "datetime",
            ColumnType.TIMESTAMP: "datetime",
            ColumnType.TIME: "time",
            ColumnType.BOOLEAN: "bool",
            ColumnType.JSON: "dict",
            ColumnType.BLOB: "bytes",
            ColumnType.LONGBLOB: "bytes",
        }
        return type_mapping.get(column_type, "str")
    
    def _has_not_null_constraint(self, column: TableColumn) -> bool:
        """检查是否有非空约束"""
        return any(c.type == ConstraintType.NOT_NULL for c in column.constraints)
    
    def _get_field_creation_function(self, column: TableColumn) -> str:
        """获取字段创建函数调用"""
        function_name, params = self._determine_field_function_and_params(column)
        
        # 构建参数列表
        param_strs = []
        for key, value in params.items():
            if isinstance(value, str):
                param_strs.append(f'{key}="{value}"')
            elif isinstance(value, bool):
                param_strs.append(f'{key}={value}')
            elif value is not None:
                param_strs.append(f'{key}={value}')
        
        if param_strs:
            return f"{function_name}({', '.join(param_strs)})"
        else:
            return f"{function_name}()"
    
    def _determine_field_function_and_params(self, column: TableColumn) -> tuple:
        """确定字段函数和参数"""
        params = {}
        
        # 添加注释
        if column.comment:
            params["comment"] = column.comment
        
        # 添加默认值
        if column.default_value:
            if column.default_value.upper() in ["CURRENT_TIMESTAMP", "NOW()"]:
                if column.type == ColumnType.DATETIME:
                    params["auto_now_add"] = True
                elif column.type == ColumnType.DATE:
                    params["auto_now_add"] = True
            else:
                # 智能处理默认值，避免重复引号
                params["default"] = self._clean_default_value(column.default_value)
        
        # 检查约束
        is_unique = any(c.type == ConstraintType.UNIQUE for c in column.constraints)
        is_primary = any(c.type == ConstraintType.PRIMARY_KEY for c in column.constraints)
        is_foreign_key = any(c.type == ConstraintType.FOREIGN_KEY for c in column.constraints)
        
        if is_unique:
            params["unique"] = True
        
        # 根据字段类型和特征选择函数
        if is_foreign_key:
            # 外键字段
            foreign_key_constraint = next((c for c in column.constraints if c.type == ConstraintType.FOREIGN_KEY), None)
            if foreign_key_constraint and foreign_key_constraint.reference_table:
                ref_table = foreign_key_constraint.reference_table
                ref_column = foreign_key_constraint.reference_column or "id"
                params = {"foreign_key": f"{ref_table}.{ref_column}", **params}
                return "create_foreign_key_column", params
        
        # 根据字段名称智能判断
        column_name_lower = column.name.lower()
        
        if "email" in column_name_lower or "mail" in column_name_lower:
            return "create_email_column", params
        elif "phone" in column_name_lower or "mobile" in column_name_lower or "tel" in column_name_lower:
            return "create_phone_column", params
        elif "url" in column_name_lower or "link" in column_name_lower or "website" in column_name_lower:
            return "create_url_column", params
        elif "status" in column_name_lower or "stat" in column_name_lower:
            return "create_status_column", params
        elif "sort" in column_name_lower or "order" in column_name_lower:
            return "create_sort_order_column", params
        elif "version" in column_name_lower or "ver" in column_name_lower:
            return "create_version_column", params
        
        # 根据数据类型选择函数
        if column.type in [ColumnType.VARCHAR, ColumnType.CHAR]:
            # 字符串类型
            if column.length:
                params["max_length"] = column.length
            
            if column.nullable and not self._has_not_null_constraint(column):
                return "create_optional_string_column", params
            else:
                return "create_required_string_column", params
                
        elif column.type == ColumnType.TEXT or column.type == ColumnType.LONGTEXT:
            return "create_text_column", params
            
        elif column.type == ColumnType.INTEGER:
            return "create_integer_column", params
            
        elif column.type == ColumnType.BIGINT:
            return "create_bigint_column", params
            
        elif column.type in [ColumnType.FLOAT, ColumnType.DOUBLE]:
            return "create_float_column", params
            
        elif column.type == ColumnType.DECIMAL:
            if column.precision:
                params["precision"] = column.precision
            if column.scale:
                params["scale"] = column.scale
            return "create_decimal_column", params
            
        elif column.type == ColumnType.BOOLEAN:
            return "create_boolean_column", params
            
        elif column.type == ColumnType.DATETIME or column.type == ColumnType.TIMESTAMP:
            return "create_datetime_column", params
            
        elif column.type == ColumnType.DATE:
            return "create_date_column", params
            
        elif column.type == ColumnType.TIME:
            return "create_time_column", params
            
        elif column.type == ColumnType.JSON:
            return "create_json_column", params
            
        elif column.type in [ColumnType.BLOB, ColumnType.LONGBLOB]:
            if column.length:
                params["max_length"] = column.length
            return "create_binary_column", params
        
        # 默认返回可选字符串字段
        return "create_optional_string_column", params
    
    def _generate_orm_column(self, column: TableColumn) -> str:
        """生成ORM列定义"""
        # 确定SQLAlchemy类型
        sa_type = self._get_sqlalchemy_type(column.type)
        
        # 构建列参数
        args = [sa_type]
        kwargs = []
        
        # 添加长度参数
        if column.length and column.type in [ColumnType.VARCHAR, ColumnType.CHAR]:
            args.append(column.length)
        
        # 添加精度参数
        if column.type == ColumnType.DECIMAL and column.precision:
            if column.scale:
                args.append(f"{column.precision}, {column.scale}")
            else:
                args.append(str(column.precision))
        
        # 添加约束
        for constraint in column.constraints:
            if constraint.type == ConstraintType.PRIMARY_KEY:
                kwargs.append("primary_key=True")
            elif constraint.type == ConstraintType.UNIQUE:
                kwargs.append("unique=True")
            elif constraint.type == ConstraintType.NOT_NULL:
                kwargs.append("nullable=False")
        
        # 添加默认值
        if column.default_value:
            if column.default_value.upper() in ["CURRENT_TIMESTAMP", "NOW()"]:
                kwargs.append("default=datetime.now")
            else:
                clean_value = self._clean_default_value(column.default_value)
                if self._is_numeric_value(str(clean_value)):
                    kwargs.append(f"default={clean_value}")
                else:
                    kwargs.append(f"default='{clean_value}'")
        
        # 添加注释
        if column.comment:
            kwargs.append(f"comment='{column.comment}'")
        
        # 构建列定义
        args_str = ", ".join([str(arg) for arg in args])
        kwargs_str = ", ".join(kwargs)
        
        if kwargs_str:
            column_def = f"    {column.name} = Column({args_str}, {kwargs_str})"
        else:
            column_def = f"    {column.name} = Column({args_str})"
        
        return column_def
    
    def _get_sqlalchemy_type(self, column_type: ColumnType) -> str:
        """获取SQLAlchemy类型"""
        type_mapping = {
            ColumnType.INTEGER: "Integer",
            ColumnType.BIGINT: "BigInteger",
            ColumnType.SMALLINT: "SmallInteger",
            ColumnType.TINYINT: "SmallInteger",
            ColumnType.FLOAT: "Float",
            ColumnType.DOUBLE: "Float",
            ColumnType.DECIMAL: "Numeric",
            ColumnType.VARCHAR: "String",
            ColumnType.CHAR: "String",
            ColumnType.TEXT: "Text",
            ColumnType.LONGTEXT: "Text",
            ColumnType.DATE: "Date",
            ColumnType.DATETIME: "DateTime",
            ColumnType.TIMESTAMP: "DateTime",
            ColumnType.TIME: "Time",
            ColumnType.BOOLEAN: "Boolean",
            ColumnType.JSON: "JSON",
            ColumnType.BLOB: "LargeBinary",
            ColumnType.LONGBLOB: "LargeBinary",
        }
        
        return type_mapping.get(column_type, "String")
    
    def _to_pascal_case(self, name: str) -> str:
        """转换为PascalCase"""
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def _clean_default_value(self, value: str) -> str:
        """清理默认值，移除多余的引号"""
        if not value:
            return value
            
        value = value.strip()
        
        # 如果被双引号包围，移除外层引号
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        
        # 如果被单引号包围，移除外层引号
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]
        
        return value
    
    def _is_numeric_value(self, value: str) -> bool:
        """检查值是否为数字（整数或小数）"""
        try:
            float(value)
            return True
        except ValueError:
            return False


class PydanticGenerator:
    """Pydantic生成器"""
    
    def generate_schema(self, table: TableDefinition) -> str:
        """生成Pydantic模式"""
        imports = [
            "from pydantic import BaseModel, Field",
            "from datetime import datetime, date, time",
            "from typing import Optional, Any",
            "from decimal import Decimal"
        ]
        
        schema_lines = [
            f"class {self._to_pascal_case(table.name)}Base(BaseModel):",
            f'    """{table.comment or f"{table.name} base schema"}"""',
            ""
        ]
        
        # 生成字段定义（跳过标准字段，避免与BaseModel冲突）
        standard_fields = {"id", "created_at", "updated_at"}
        for column in table.columns:
            if column.name not in standard_fields:
                schema_lines.append(self._generate_pydantic_field(column))
        
        # 生成完整的CRUD模式
        schema_lines.extend([
            "",
            f"class {self._to_pascal_case(table.name)}Create({self._to_pascal_case(table.name)}Base):",
            '    """创建时使用的模式"""',
            "    pass",
            "",
            f"class {self._to_pascal_case(table.name)}Update({self._to_pascal_case(table.name)}Base):",
            '    """更新时使用的模式（所有字段都是可选的）"""',
            "    pass",
            "",
            f"class {self._to_pascal_case(table.name)}Response({self._to_pascal_case(table.name)}Base):",
            '    """API响应时使用的模式"""',
            "    id: str  # PyAdvanceKit使用UUID作为主键",
            "    created_at: datetime",
            "    updated_at: datetime",
            "",
            "    class Config:",
            "        from_attributes = True",
            "",
            f"class {self._to_pascal_case(table.name)}InDB({self._to_pascal_case(table.name)}Response):",
            '    """数据库存储模式（包含所有字段）"""',
            "    pass",
            "",
            f"class {self._to_pascal_case(table.name)}Query(BaseModel):",
            '    """查询参数模式"""',
            "    page: Optional[int] = Field(default=1, ge=1, description='页码')",
            "    size: Optional[int] = Field(default=10, ge=1, le=100, description='每页数量')",
            "    search: Optional[str] = Field(default=None, description='搜索关键词')",
            "    order_by: Optional[str] = Field(default=None, description='排序字段')",
            "    order_desc: Optional[bool] = Field(default=False, description='是否降序')",
            "",
            f"class {self._to_pascal_case(table.name)}Filter(BaseModel):",
            '    """过滤条件模式"""',
            "    # 可以根据需要添加具体的过滤字段",
        ])
        
        # 为常见的过滤字段添加过滤条件
        filter_fields = []
        for column in table.columns:
            if self._is_filterable_field(column):
                filter_fields.append(self._generate_filter_field(column))
        
        if filter_fields:
            schema_lines.extend(filter_fields)
        else:
            schema_lines.append("    pass")
        
        return "\n".join(imports + [""] + schema_lines)
    
    def _is_filterable_field(self, column: TableColumn) -> bool:
        """判断字段是否适合作为过滤条件"""
        # 排除一些不适合过滤的字段类型
        exclude_types = [ColumnType.TEXT, ColumnType.LONGTEXT, ColumnType.BLOB, ColumnType.LONGBLOB]
        if column.type in exclude_types:
            return False
        
        # 排除一些不适合过滤的字段名
        exclude_names = ['created_at', 'updated_at', 'deleted_at', 'password', 'token']
        if column.name.lower() in exclude_names:
            return False
        
        # 常见的过滤字段
        filter_keywords = ['status', 'type', 'category', 'level', 'priority', 'state']
        column_name_lower = column.name.lower()
        
        return any(keyword in column_name_lower for keyword in filter_keywords)
    
    def _generate_filter_field(self, column: TableColumn) -> str:
        """生成过滤字段"""
        python_type = self._get_python_type(column.type)
        field_name = f"{column.name.lower()}_filter"
        
        if column.type in [ColumnType.INTEGER, ColumnType.BIGINT]:
            # 数值类型支持范围过滤
            return f"    {field_name}_min: Optional[{python_type}] = Field(default=None, description='{column.comment or column.name}最小值')"
        elif column.type in [ColumnType.VARCHAR, ColumnType.CHAR]:
            # 字符串类型支持模糊匹配
            return f"    {field_name}: Optional[{python_type}] = Field(default=None, description='{column.comment or column.name}过滤')"
        elif column.type == ColumnType.BOOLEAN:
            # 布尔类型直接过滤
            return f"    {field_name}: Optional[{python_type}] = Field(default=None, description='{column.comment or column.name}过滤')"
        else:
            # 其他类型
            return f"    {field_name}: Optional[{python_type}] = Field(default=None, description='{column.comment or column.name}过滤')"
    
    def _generate_pydantic_field(self, column: TableColumn) -> str:
        """生成Pydantic字段"""
        # 确定Python类型
        python_type = self._get_python_type(column.type)
        
        # 处理可选字段
        if column.nullable:
            python_type = f"Optional[{python_type}]"
        
        # 构建字段定义
        field_parts = [f"    {column.name}: {python_type}"]
        
        # 添加Field参数
        field_kwargs = []
        
        # 首先添加默认值参数（必须在最前面）
        if not column.nullable:
            field_kwargs.append("...")  # 必需字段  
        else:
            field_kwargs.append("default=None")  # 可选字段
        
        # 然后添加其他参数
        if column.comment:
            field_kwargs.append(f"description='{column.comment}'")
        
        if field_kwargs:
            field_parts.append(f" = Field({', '.join(field_kwargs)})")
        
        return "".join(field_parts)
    
    def _get_python_type(self, column_type: ColumnType) -> str:
        """获取Python类型"""
        type_mapping = {
            ColumnType.INTEGER: "int",
            ColumnType.BIGINT: "int",
            ColumnType.SMALLINT: "int",
            ColumnType.TINYINT: "int",
            ColumnType.FLOAT: "float",
            ColumnType.DOUBLE: "float",
            ColumnType.DECIMAL: "Decimal",
            ColumnType.VARCHAR: "str",
            ColumnType.CHAR: "str",
            ColumnType.TEXT: "str",
            ColumnType.LONGTEXT: "str",
            ColumnType.DATE: "date",
            ColumnType.DATETIME: "datetime",
            ColumnType.TIMESTAMP: "datetime",
            ColumnType.TIME: "time",
            ColumnType.BOOLEAN: "bool",
            ColumnType.JSON: "Any",
            ColumnType.BLOB: "bytes",
            ColumnType.LONGBLOB: "bytes",
        }
        
        return type_mapping.get(column_type, "str")
    
    def _to_pascal_case(self, name: str) -> str:
        """转换为PascalCase"""
        return ''.join(word.capitalize() for word in name.split('_'))


class ExcelCodeGenerator:
    """Excel代码生成器"""
    
    def __init__(self):
        self.parser = ExcelParser()
        self.sql_generator = SQLGenerator()
        self.orm_generator = ORMGenerator()
        self.pydantic_generator = PydanticGenerator()
    
    def generate_from_excel(
        self,
        excel_file: str,
        output_dir: str,
        generate_sql: bool = True,
        generate_orm: bool = True,
        generate_pydantic: bool = True
    ) -> Dict[str, str]:
        """从Excel文件生成代码"""
        # 解析Excel文件
        design = self.parser.parse_excel_file(excel_file)
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        generated_files = {}
        
        # 生成SQL
        if generate_sql:
            sql_content = self.sql_generator.generate_all_sql(design)
            sql_file = os.path.join(output_dir, f"{design.name}.sql")
            with open(sql_file, 'w', encoding='utf-8') as f:
                f.write(sql_content)
            generated_files['sql'] = sql_file
            logger.info(f"Generated SQL file: {sql_file}")
        
        # 生成ORM模型
        if generate_orm:
            orm_content = self._generate_all_orm_models(design)
            orm_file = os.path.join(output_dir, "models.py")
            with open(orm_file, 'w', encoding='utf-8') as f:
                f.write(orm_content)
            generated_files['orm'] = orm_file
            logger.info(f"Generated ORM file: {orm_file}")
        
        # 生成Pydantic模式
        if generate_pydantic:
            pydantic_content = self._generate_all_pydantic_schemas(design)
            pydantic_file = os.path.join(output_dir, "schemas.py")
            with open(pydantic_file, 'w', encoding='utf-8') as f:
                f.write(pydantic_content)
            generated_files['pydantic'] = pydantic_file
            logger.info(f"Generated Pydantic file: {pydantic_file}")
        
        return generated_files
    
    def _generate_all_orm_models(self, design: DatabaseDesign) -> str:
        """生成所有ORM模型"""
        content_parts = [
            "#!/usr/bin/env python3",
            '"""',
            f"Generated ORM models for {design.name}",
            f"Generated at: {datetime.now().isoformat()}",
            '"""',
            "",
            "from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, JSON, Date, Time, Numeric, BigInteger, SmallInteger, LargeBinary",
            "from sqlalchemy.ext.declarative import declarative_base",
            "from pyadvincekit.models.base import BaseModel",
            "from datetime import datetime, date, time",
            "from typing import Optional",
            "",
            "Base = declarative_base()",
            ""
        ]
        
        for table in design.tables:
            content_parts.append(self.orm_generator.generate_model(table))
            content_parts.append("")
        
        return "\n".join(content_parts)
    
    def _generate_all_pydantic_schemas(self, design: DatabaseDesign) -> str:
        """生成所有Pydantic模式"""
        content_parts = [
            "#!/usr/bin/env python3",
            '"""',
            f"Generated Pydantic schemas for {design.name}",
            f"Generated at: {datetime.now().isoformat()}",
            '"""',
            "",
            "from pydantic import BaseModel, Field",
            "from datetime import datetime, date, time",
            "from typing import Optional, Any",
            "from decimal import Decimal",
            ""
        ]
        
        for table in design.tables:
            content_parts.append(self.pydantic_generator.generate_schema(table))
            content_parts.append("")
        
        return "\n".join(content_parts)


# 便捷函数
def generate_from_excel(
    excel_file: str,
    output_dir: str,
    generate_sql: bool = True,
    generate_orm: bool = True,
    generate_pydantic: bool = True
) -> Dict[str, str]:
    """从Excel文件生成代码的便捷函数"""
    generator = ExcelCodeGenerator()
    return generator.generate_from_excel(
        excel_file=excel_file,
        output_dir=output_dir,
        generate_sql=generate_sql,
        generate_orm=generate_orm,
        generate_pydantic=generate_pydantic
    )
