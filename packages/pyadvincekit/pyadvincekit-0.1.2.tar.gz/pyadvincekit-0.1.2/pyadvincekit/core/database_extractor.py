#!/usr/bin/env python3
"""
数据库元数据提取器

从数据库中提取表结构、字段、约束、索引等元数据信息，
转换为 PyAdvanceKit 的 DatabaseDesign 对象
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from pyadvincekit.logging import get_logger
from pyadvincekit.core.database import DatabaseManager, get_database_manager
from pyadvincekit.core.config import Settings, get_settings
from pyadvincekit.core.excel_generator import (
    ColumnType, ConstraintType, ColumnConstraint, TableColumn, 
    TableDefinition, DatabaseDesign, TableIndex
)

logger = get_logger(__name__)


class DatabaseTypeMapper:
    """数据库类型到PyAdvanceKit类型的映射器"""
    
    # MySQL类型映射
    MYSQL_TYPE_MAPPING = {
        # 整数类型
        'tinyint': ColumnType.TINYINT,
        'smallint': ColumnType.SMALLINT,
        'mediumint': ColumnType.INTEGER,
        'int': ColumnType.INTEGER,
        'integer': ColumnType.INTEGER,
        'bigint': ColumnType.BIGINT,
        
        # 浮点类型
        'float': ColumnType.FLOAT,
        'double': ColumnType.DOUBLE,
        'decimal': ColumnType.DECIMAL,
        'numeric': ColumnType.DECIMAL,
        
        # 字符串类型
        'char': ColumnType.CHAR,
        'varchar': ColumnType.VARCHAR,
        'text': ColumnType.TEXT,
        'tinytext': ColumnType.TEXT,
        'mediumtext': ColumnType.TEXT,
        'longtext': ColumnType.LONGTEXT,
        
        # 日期时间类型
        'date': ColumnType.DATE,
        'time': ColumnType.TIME,
        'datetime': ColumnType.DATETIME,
        'timestamp': ColumnType.TIMESTAMP,
        'year': ColumnType.INTEGER,
        
        # 布尔类型
        'boolean': ColumnType.BOOLEAN,
        'bool': ColumnType.BOOLEAN,
        
        # 二进制类型
        'binary': ColumnType.BLOB,
        'varbinary': ColumnType.BLOB,
        'blob': ColumnType.BLOB,
        'tinyblob': ColumnType.BLOB,
        'mediumblob': ColumnType.BLOB,
        'longblob': ColumnType.LONGBLOB,
        
        # JSON类型
        'json': ColumnType.JSON,
    }
    
    # PostgreSQL类型映射
    POSTGRESQL_TYPE_MAPPING = {
        # 整数类型
        'smallint': ColumnType.SMALLINT,
        'integer': ColumnType.INTEGER,
        'int': ColumnType.INTEGER,
        'int4': ColumnType.INTEGER,
        'bigint': ColumnType.BIGINT,
        'int8': ColumnType.BIGINT,
        'serial': ColumnType.INTEGER,
        'bigserial': ColumnType.BIGINT,
        
        # 浮点类型
        'real': ColumnType.FLOAT,
        'float4': ColumnType.FLOAT,
        'double precision': ColumnType.DOUBLE,
        'float8': ColumnType.DOUBLE,
        'numeric': ColumnType.DECIMAL,
        'decimal': ColumnType.DECIMAL,
        
        # 字符串类型
        'character': ColumnType.CHAR,
        'char': ColumnType.CHAR,
        'character varying': ColumnType.VARCHAR,
        'varchar': ColumnType.VARCHAR,
        'text': ColumnType.TEXT,
        
        # 日期时间类型
        'date': ColumnType.DATE,
        'time': ColumnType.TIME,
        'timestamp': ColumnType.TIMESTAMP,
        'timestamptz': ColumnType.TIMESTAMP,
        'interval': ColumnType.VARCHAR,
        
        # 布尔类型
        'boolean': ColumnType.BOOLEAN,
        'bool': ColumnType.BOOLEAN,
        
        # JSON类型
        'json': ColumnType.JSON,
        'jsonb': ColumnType.JSON,
        
        # 二进制类型
        'bytea': ColumnType.BLOB,
        
        # UUID类型
        'uuid': ColumnType.VARCHAR,
    }
    
    # SQLite类型映射
    SQLITE_TYPE_MAPPING = {
        # 整数类型
        'integer': ColumnType.INTEGER,
        'int': ColumnType.INTEGER,
        'tinyint': ColumnType.TINYINT,
        'smallint': ColumnType.SMALLINT,
        'mediumint': ColumnType.INTEGER,
        'bigint': ColumnType.BIGINT,
        
        # 浮点类型
        'real': ColumnType.FLOAT,
        'double': ColumnType.DOUBLE,
        'float': ColumnType.FLOAT,
        'numeric': ColumnType.DECIMAL,
        'decimal': ColumnType.DECIMAL,
        
        # 字符串类型
        'text': ColumnType.TEXT,
        'varchar': ColumnType.VARCHAR,
        'char': ColumnType.CHAR,
        'character': ColumnType.CHAR,
        
        # 日期时间类型
        'date': ColumnType.DATE,
        'datetime': ColumnType.DATETIME,
        'timestamp': ColumnType.TIMESTAMP,
        
        # 布尔类型
        'boolean': ColumnType.BOOLEAN,
        'bool': ColumnType.BOOLEAN,
        
        # 二进制类型
        'blob': ColumnType.BLOB,
    }
    
    @classmethod
    def map_type(cls, db_type: str, column_type: str, db_name: str = "mysql") -> ColumnType:
        """
        映射数据库类型到PyAdvanceKit类型
        
        Args:
            db_type: 数据库类型 (mysql, postgresql, sqlite)
            column_type: 数据库中的列类型
            db_name: 数据库名称（用于日志）
        
        Returns:
            PyAdvanceKit的ColumnType
        """
        # 清理类型名称（去除长度等信息）
        clean_type = re.sub(r'\([^)]*\)', '', column_type.lower().strip())
        
        # 选择对应的映射表
        if db_type == "mysql":
            mapping = cls.MYSQL_TYPE_MAPPING
        elif db_type == "postgresql":
            mapping = cls.POSTGRESQL_TYPE_MAPPING
        elif db_type == "sqlite":
            mapping = cls.SQLITE_TYPE_MAPPING
        else:
            logger.warning(f"Unsupported database type: {db_type}")
            mapping = cls.MYSQL_TYPE_MAPPING  # 默认使用MySQL映射
        
        # 查找映射
        if clean_type in mapping:
            return mapping[clean_type]
        
        # 特殊处理一些类型
        if 'int' in clean_type:
            return ColumnType.INTEGER
        elif 'char' in clean_type or 'text' in clean_type:
            return ColumnType.VARCHAR
        elif 'float' in clean_type or 'double' in clean_type:
            return ColumnType.FLOAT
        elif 'decimal' in clean_type or 'numeric' in clean_type:
            return ColumnType.DECIMAL
        elif 'date' in clean_type:
            return ColumnType.DATE
        elif 'time' in clean_type:
            return ColumnType.DATETIME
        elif 'bool' in clean_type:
            return ColumnType.BOOLEAN
        elif 'blob' in clean_type or 'binary' in clean_type:
            return ColumnType.BLOB
        elif 'json' in clean_type:
            return ColumnType.JSON
        
        # 如果找不到映射，记录警告并默认为VARCHAR
        logger.warning(f"Unknown column type '{column_type}' in database '{db_name}', mapping to VARCHAR")
        return ColumnType.VARCHAR


class DatabaseMetadataExtractor:
    """数据库元数据提取器"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        初始化提取器
        
        Args:
            database_url: 可选的数据库连接URL，如果不提供则使用PyAdvanceKit配置
        """
        if database_url:
            # 创建临时配置
            settings = get_settings()
            self.temp_settings = Settings()
            # 复制其他设置
            for key, value in settings.__dict__.items():
                if hasattr(self.temp_settings, key):
                    setattr(self.temp_settings, key, value)
            # 设置新的数据库URL
            self.temp_settings.database_url = database_url
            
            # 创建临时数据库管理器
            self.db_manager = DatabaseManager(self.temp_settings)
        else:
            # 使用默认的数据库管理器
            self.db_manager = get_database_manager()
    
    async def extract_database_design(self, database_name: Optional[str] = None) -> DatabaseDesign:
        """
        提取数据库设计
        
        Args:
            database_name: 数据库名称
        
        Returns:
            DatabaseDesign对象
        """
        logger.info(f"Extracting database design from database")
        
        design = DatabaseDesign(name=database_name or "extracted_database")
        
        # 使用PyAdvanceKit的数据库会话
        async with self.db_manager.get_session() as session:
            # 获取数据库类型
            db_type = self._get_database_type()
            logger.info(f"Detected database type: {db_type}")
            
            # 获取所有表
            tables = await self._get_all_tables(session, db_type)
            logger.info(f"Found {len(tables)} tables")
            
            for table_name in tables:
                logger.info(f"Extracting table: {table_name}")
                table_def = await self._extract_table_definition(session, table_name, db_type)
                if table_def:
                    design.tables.append(table_def)
        
        logger.info(f"Extracted {len(design.tables)} tables from database")
        return design
    
    def _get_database_type(self) -> str:
        """获取数据库类型"""
        engine = self.db_manager.engine
        db_url = str(engine.url)
        
        if "mysql" in db_url or "pymysql" in db_url:
            return "mysql"
        elif "postgresql" in db_url or "psycopg" in db_url:
            return "postgresql"
        elif "sqlite" in db_url:
            return "sqlite"
        else:
            logger.warning(f"Unknown database type from URL: {db_url}")
            return "unknown"
    
    async def _get_all_tables(self, session: AsyncSession, db_type: str) -> List[str]:
        """获取所有表名"""
        if db_type == "mysql":
            query = text("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)
        elif db_type == "postgresql":
            query = text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """)
        elif db_type == "sqlite":
            query = text("""
                SELECT name 
                FROM sqlite_master 
                WHERE type = 'table' 
                AND name NOT LIKE 'sqlite_%'
                AND name NOT LIKE 'alembic_%'
                ORDER BY name
            """)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        result = await session.execute(query)
        return [row[0] for row in result.fetchall()]
    
    async def _extract_table_definition(self, session: AsyncSession, table_name: str, db_type: str) -> Optional[TableDefinition]:
        """提取表定义"""
        try:
            # 获取表的列信息
            columns = await self._get_table_columns(session, table_name, db_type)
            
            # 获取表的约束信息并合并到对应的列上
            constraints = await self._get_table_constraints(session, table_name, db_type)
            self._merge_constraints_to_columns(columns, constraints)
            
            # 获取表的索引信息
            indexes = await self._get_table_indexes(session, table_name, db_type)
            
            # 获取表注释
            table_comment = await self._get_table_comment(session, table_name, db_type)
            
            return TableDefinition(
                name=table_name,
                comment=table_comment or f"Table {table_name}",
                columns=columns,
                indexes=indexes
            )
            
        except Exception as e:
            logger.error(f"Failed to extract table {table_name}: {e}")
            return None
    
    def _merge_constraints_to_columns(self, columns: List[TableColumn], constraints_by_column: Dict[str, List[ColumnConstraint]]):
        """将约束信息合并到对应的列上"""
        for column in columns:
            if column.name in constraints_by_column:
                column.constraints.extend(constraints_by_column[column.name])
    
    async def _get_table_columns(self, session: AsyncSession, table_name: str, db_type: str) -> List[TableColumn]:
        """获取表的列信息"""
        columns = []
        
        if db_type == "mysql":
            query = text("""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE,
                    COLUMN_DEFAULT,
                    CHARACTER_MAXIMUM_LENGTH,
                    NUMERIC_PRECISION,
                    NUMERIC_SCALE,
                    COLUMN_COMMENT,
                    EXTRA
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = :table_name
                ORDER BY ORDINAL_POSITION
            """)
        elif db_type == "postgresql":
            query = text("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale,
                    '' as column_comment,
                    '' as extra
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = :table_name
                ORDER BY ordinal_position
            """)
        elif db_type == "sqlite":
            query = text(f"PRAGMA table_info({table_name})")
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        if db_type == "sqlite":
            result = await session.execute(query)
            for row in result.fetchall():
                # SQLite PRAGMA返回: cid, name, type, notnull, dflt_value, pk
                column_name = row[1]
                data_type = row[2]
                is_nullable = "YES" if row[3] == 0 else "NO"
                column_default = row[4]
                is_primary_key = row[5] == 1
                
                # 映射类型
                column_type = DatabaseTypeMapper.map_type(db_type, data_type, table_name)
                
                # 提取长度信息
                length = self._extract_length_from_type(data_type)
                
                column = TableColumn(
                    name=column_name,
                    type=column_type,
                    length=length,
                    nullable=is_nullable == "YES",
                    default_value=column_default,
                    comment=""
                )
                columns.append(column)
        else:
            result = await session.execute(query, {"table_name": table_name})
            for row in result.fetchall():
                column_name = row[0]
                data_type = row[1]
                is_nullable = row[2]
                column_default = row[3]
                max_length = row[4]
                precision = row[5]
                scale = row[6]
                comment = row[7] if len(row) > 7 else ""
                extra = row[8] if len(row) > 8 else ""
                
                # 映射类型
                column_type = DatabaseTypeMapper.map_type(db_type, data_type, table_name)
                
                # 确定长度
                if max_length:
                    length = max_length
                elif precision:
                    if scale and scale > 0:
                        length = f"{precision},{scale}"
                    else:
                        length = precision
                else:
                    length = None
                
                column = TableColumn(
                    name=column_name,
                    type=column_type,
                    length=length,
                    nullable=is_nullable == "YES",
                    default_value=column_default,
                    comment=comment or ""
                )
                columns.append(column)
        
        return columns
    
    def _extract_length_from_type(self, data_type: str) -> Optional[int]:
        """从数据类型字符串中提取长度信息"""
        match = re.search(r'\((\d+)\)', data_type)
        if match:
            return int(match.group(1))
        return None
    
    async def _get_table_constraints(self, session: AsyncSession, table_name: str, db_type: str) -> Dict[str, List[ColumnConstraint]]:
        """获取表的约束信息，返回按列名分组的约束字典"""
        constraints_by_column = {}
        
        if db_type == "mysql":
            # 获取主键和唯一约束
            query = text("""
                SELECT 
                    kcu.COLUMN_NAME,
                    tc.CONSTRAINT_TYPE,
                    kcu.CONSTRAINT_NAME
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu 
                ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
                WHERE tc.TABLE_SCHEMA = DATABASE()
                AND tc.TABLE_NAME = :table_name
                AND tc.CONSTRAINT_TYPE IN ('PRIMARY KEY', 'UNIQUE')
            """)
            
            result = await session.execute(query, {"table_name": table_name})
            for row in result.fetchall():
                column_name = row[0]
                constraint_type = row[1]
                constraint_name = row[2]
                
                if constraint_type == "PRIMARY KEY":
                    constraint = ColumnConstraint(
                        type=ConstraintType.PRIMARY_KEY
                    )
                elif constraint_type == "UNIQUE":
                    constraint = ColumnConstraint(
                        type=ConstraintType.UNIQUE
                    )
                else:
                    continue
                
                if column_name not in constraints_by_column:
                    constraints_by_column[column_name] = []
                constraints_by_column[column_name].append(constraint)
        
        # 其他数据库类型的约束查询可以后续添加
        
        return constraints_by_column
    
    async def _get_table_indexes(self, session: AsyncSession, table_name: str, db_type: str) -> List[TableIndex]:
        """获取表的索引信息"""
        indexes = []
        
        if db_type == "mysql":
            query = text("""
                SELECT 
                    INDEX_NAME,
                    COLUMN_NAME,
                    NON_UNIQUE,
                    SEQ_IN_INDEX
                FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = :table_name
                AND INDEX_NAME != 'PRIMARY'
                ORDER BY INDEX_NAME, SEQ_IN_INDEX
            """)
            
            result = await session.execute(query, {"table_name": table_name})
            
            # 按索引名分组
            index_dict = {}
            for row in result.fetchall():
                index_name = row[0]
                column_name = row[1]
                non_unique = row[2]
                
                if index_name not in index_dict:
                    index_dict[index_name] = {
                        'columns': [],
                        'unique': non_unique == 0
                    }
                
                index_dict[index_name]['columns'].append(column_name)
            
            # 创建索引对象
            for index_name, info in index_dict.items():
                index = TableIndex(
                    name=index_name,
                    columns=info['columns'],
                    unique=info['unique']
                )
                indexes.append(index)
        
        return indexes
    
    async def _get_table_comment(self, session: AsyncSession, table_name: str, db_type: str) -> Optional[str]:
        """获取表注释"""
        if db_type == "mysql":
            query = text("""
                SELECT TABLE_COMMENT
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = :table_name
            """)
            
            result = await session.execute(query, {"table_name": table_name})
            row = result.fetchone()
            if row and row[0]:
                return row[0]
        
        return None



