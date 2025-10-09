#!/usr/bin/env python3
"""
统一代码生成器

整合Excel解析、SQL生成、ORM生成、Pydantic生成功能
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime

from pyadvincekit.logging import get_logger
from pyadvincekit.core.excel_parser import DatabaseDesignParser, parse_database_design_excel
from pyadvincekit.core.excel_generator import (
    SQLGenerator, ORMGenerator, PydanticGenerator, DatabaseDesign
)

logger = get_logger(__name__)


class DatabaseCodeGenerator:
    """数据库代码生成器"""
    
    def __init__(self, add_standard_fields: bool = True):
        self.parser = DatabaseDesignParser(add_standard_fields=add_standard_fields)
        self.sql_generator = SQLGenerator()
        self.orm_generator = ORMGenerator()
        self.pydantic_generator = PydanticGenerator()
    
    def generate_from_excel(
        self,
        excel_file: str,
        output_dir: str,
        generate_sql: bool = True,
        generate_orm: bool = True,
        generate_pydantic: bool = True,
        database_name: Optional[str] = None
    ) -> Dict[str, str]:
        """从Excel文件生成所有代码"""
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 解析Excel文件
        logger.info(f"Parsing Excel file: {excel_file}")
        design = self.parser.parse_excel_file(excel_file)
        
        # 如果指定了数据库名称，更新设计
        if database_name:
            design.name = database_name
        
        generated_files = {}
        
        # 生成SQL
        if generate_sql:
            sql_content = self._generate_sql(design)
            sql_file = os.path.join(output_dir, f"{design.name}.sql")
            with open(sql_file, 'w', encoding='utf-8') as f:
                f.write(sql_content)
            generated_files['sql'] = sql_file
            logger.info(f"Generated SQL file: {sql_file}")
        
        # 生成ORM模型
        if generate_orm:
            orm_content = self._generate_orm(design)
            orm_file = os.path.join(output_dir, "models.py")
            with open(orm_file, 'w', encoding='utf-8') as f:
                f.write(orm_content)
            generated_files['orm'] = orm_file
            logger.info(f"Generated ORM file: {orm_file}")
        
        # 生成Pydantic模式
        if generate_pydantic:
            pydantic_content = self._generate_pydantic(design)
            pydantic_file = os.path.join(output_dir, "schemas.py")
            with open(pydantic_file, 'w', encoding='utf-8') as f:
                f.write(pydantic_content)
            generated_files['pydantic'] = pydantic_file
            logger.info(f"Generated Pydantic file: {pydantic_file}")
        
        return generated_files
    
    def _generate_sql(self, design: DatabaseDesign) -> str:
        """生成SQL"""
        # 生成表结构SQL（不包含CREATE DATABASE）
        sql_parts = []
        for table in design.tables:
            table_sql = self.sql_generator.generate_create_table_sql(table)
            sql_parts.append(table_sql)
        
        return "\n".join(sql_parts)
    
    def _generate_orm(self, design: DatabaseDesign) -> str:
        """生成ORM模型"""
        content_parts = [
            "#!/usr/bin/env python3",
            '"""',
            f"Generated ORM models for {design.name}",
            f"Generated at: {datetime.now().isoformat()}",
            '"""',
            "",
            "from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, JSON, Date, Time, Numeric, BigInteger, SmallInteger, LargeBinary",
            "from sqlalchemy.ext.declarative import declarative_base",
            "from sqlalchemy.orm import Mapped",
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
    
    def _generate_pydantic(self, design: DatabaseDesign) -> str:
        """生成Pydantic模式"""
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
    
    def generate_sql_only(self, excel_file: str, output_file: str) -> str:
        """只生成SQL文件"""
        design = self.parser.parse_excel_file(excel_file)
        sql_content = self._generate_sql(design)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        
        logger.info(f"Generated SQL file: {output_file}")
        return sql_content
    
    def generate_orm_only(self, excel_file: str, output_file: str) -> str:
        """只生成ORM文件"""
        design = self.parser.parse_excel_file(excel_file)
        orm_content = self._generate_orm(design)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(orm_content)
        
        logger.info(f"Generated ORM file: {output_file}")
        return orm_content
    
    def generate_pydantic_only(self, excel_file: str, output_file: str) -> str:
        """只生成Pydantic文件"""
        design = self.parser.parse_excel_file(excel_file)
        pydantic_content = self._generate_pydantic(design)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(pydantic_content)
        
        logger.info(f"Generated Pydantic file: {output_file}")
        return pydantic_content
    
    def generate_separate_files(
        self,
        excel_file: str,
        output_dir: str,
        orm_output_dir: Optional[str] = None,
        schema_output_dir: Optional[str] = None,
        sql_output_dir: Optional[str] = None,
        generate_sql: bool = True,
        generate_orm: bool = True,
        generate_pydantic: bool = True,
        database_name: Optional[str] = None,
        auto_init_files: bool = True
    ) -> Dict[str, Any]:
        """
        按表分别生成文件到指定目录
        
        Args:
            excel_file: Excel文件路径
            output_dir: 默认输出目录
            orm_output_dir: ORM文件输出目录
            schema_output_dir: Schema文件输出目录
            sql_output_dir: SQL文件输出目录
            generate_sql: 是否生成SQL
            generate_orm: 是否生成ORM
            generate_pydantic: 是否生成Pydantic
            database_name: 数据库名称
            auto_init_files: 是否自动生成__init__.py文件
        
        Returns:
            生成文件信息的字典
        """
        
        # 解析Excel文件
        logger.info(f"Parsing Excel file: {excel_file}")
        design = self.parser.parse_excel_file(excel_file)
        
        # 如果指定了数据库名称，更新设计
        if database_name:
            design.name = database_name
        
        # 确定各个输出目录
        final_orm_dir = orm_output_dir or os.path.join(output_dir, "models")
        final_schema_dir = schema_output_dir or os.path.join(output_dir, "schemas")
        final_sql_dir = sql_output_dir or os.path.join(output_dir, "sql")
        
        # 创建输出目录
        if generate_orm:
            os.makedirs(final_orm_dir, exist_ok=True)
        if generate_pydantic:
            os.makedirs(final_schema_dir, exist_ok=True)
        if generate_sql:
            os.makedirs(final_sql_dir, exist_ok=True)
        
        generated_files = {
            "orm_files": [],
            "schema_files": [],
            "sql_files": [],
            "init_files": []
        }
        
        # 生成SQL文件
        if generate_sql:
            sql_files = self._generate_separate_sql_files(design, final_sql_dir)
            generated_files["sql_files"].extend(sql_files)
        
        # 生成ORM文件
        if generate_orm:
            orm_files = self._generate_separate_orm_files(design, final_orm_dir)
            generated_files["orm_files"].extend(orm_files)
            
            # 生成ORM __init__.py
            if auto_init_files:
                orm_init_file = self._generate_orm_init_file(design, final_orm_dir)
                generated_files["init_files"].append(orm_init_file)
        
        # 生成Pydantic文件
        if generate_pydantic:
            schema_files = self._generate_separate_schema_files(design, final_schema_dir)
            generated_files["schema_files"].extend(schema_files)
            
            # 生成Schema __init__.py
            if auto_init_files:
                schema_init_file = self._generate_schema_init_file(design, final_schema_dir)
                generated_files["init_files"].append(schema_init_file)
        
        logger.info(f"Generated {len(generated_files['orm_files'])} ORM files, "
                   f"{len(generated_files['schema_files'])} schema files, "
                   f"{len(generated_files['sql_files'])} SQL files")
        
        return generated_files
    
    def generate_from_design(
        self,
        design: DatabaseDesign,
        output_dir: str,
        generate_sql: bool = True,
        generate_orm: bool = True,
        generate_pydantic: bool = True
    ) -> Dict[str, str]:
        """
        从DatabaseDesign对象生成代码（单文件模式）
        
        Args:
            design: 数据库设计对象
            output_dir: 输出目录
            generate_sql: 是否生成SQL
            generate_orm: 是否生成ORM
            generate_pydantic: 是否生成Pydantic
        
        Returns:
            生成文件信息的字典
        """
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        generated_files = {}
        
        # 生成SQL
        if generate_sql:
            sql_content = self._generate_sql(design)
            sql_file = os.path.join(output_dir, f"{design.name}.sql")
            with open(sql_file, 'w', encoding='utf-8') as f:
                f.write(sql_content)
            generated_files['sql'] = sql_file
            logger.info(f"Generated SQL file: {sql_file}")
        
        # 生成ORM模型
        if generate_orm:
            orm_content = self._generate_orm(design)
            orm_file = os.path.join(output_dir, "models.py")
            with open(orm_file, 'w', encoding='utf-8') as f:
                f.write(orm_content)
            generated_files['orm'] = orm_file
            logger.info(f"Generated ORM file: {orm_file}")
        
        # 生成Pydantic模式
        if generate_pydantic:
            pydantic_content = self._generate_pydantic(design)
            pydantic_file = os.path.join(output_dir, "schemas.py")
            with open(pydantic_file, 'w', encoding='utf-8') as f:
                f.write(pydantic_content)
            generated_files['pydantic'] = pydantic_file
            logger.info(f"Generated Pydantic file: {pydantic_file}")
        
        return generated_files
    
    def generate_separate_files_from_design(
        self,
        design: DatabaseDesign,
        output_dir: str,
        orm_output_dir: Optional[str] = None,
        schema_output_dir: Optional[str] = None,
        sql_output_dir: Optional[str] = None,
        generate_sql: bool = True,
        generate_orm: bool = True,
        generate_pydantic: bool = True,
        auto_init_files: bool = True
    ) -> Dict[str, Any]:
        """
        从DatabaseDesign对象按表分别生成文件到指定目录
        
        Args:
            design: 数据库设计对象
            output_dir: 默认输出目录
            orm_output_dir: ORM文件输出目录
            schema_output_dir: Schema文件输出目录
            sql_output_dir: SQL文件输出目录
            generate_sql: 是否生成SQL
            generate_orm: 是否生成ORM
            generate_pydantic: 是否生成Pydantic
            auto_init_files: 是否自动生成__init__.py文件
        
        Returns:
            生成文件信息的字典
        """
        
        # 确定各个输出目录
        final_orm_dir = orm_output_dir or os.path.join(output_dir, "models")
        final_schema_dir = schema_output_dir or os.path.join(output_dir, "schemas")
        final_sql_dir = sql_output_dir or os.path.join(output_dir, "sql")
        
        # 创建输出目录
        if generate_orm:
            os.makedirs(final_orm_dir, exist_ok=True)
        if generate_pydantic:
            os.makedirs(final_schema_dir, exist_ok=True)
        if generate_sql:
            os.makedirs(final_sql_dir, exist_ok=True)
        
        generated_files = {
            "orm_files": [],
            "schema_files": [],
            "sql_files": [],
            "init_files": []
        }
        
        # 生成SQL文件
        if generate_sql:
            sql_files = self._generate_separate_sql_files(design, final_sql_dir)
            generated_files["sql_files"].extend(sql_files)
        
        # 生成ORM文件
        if generate_orm:
            orm_files = self._generate_separate_orm_files(design, final_orm_dir)
            generated_files["orm_files"].extend(orm_files)
            
            # 生成ORM __init__.py
            if auto_init_files:
                orm_init_file = self._generate_orm_init_file(design, final_orm_dir)
                generated_files["init_files"].append(orm_init_file)
        
        # 生成Pydantic文件
        if generate_pydantic:
            schema_files = self._generate_separate_schema_files(design, final_schema_dir)
            generated_files["schema_files"].extend(schema_files)
            
            # 生成Schema __init__.py
            if auto_init_files:
                schema_init_file = self._generate_schema_init_file(design, final_schema_dir)
                generated_files["init_files"].append(schema_init_file)
        
        logger.info(f"Generated {len(generated_files['orm_files'])} ORM files, "
                   f"{len(generated_files['schema_files'])} schema files, "
                   f"{len(generated_files['sql_files'])} SQL files")
        
        return generated_files
    
    def _generate_separate_sql_files(self, design: DatabaseDesign, output_dir: str) -> List[str]:
        """生成分离的SQL文件"""
        generated_files = []
        
        # 生成主SQL文件（包含所有表）
        main_sql_content = []
        for table in design.tables:
            table_sql = self.sql_generator.generate_create_table_sql(table)
            main_sql_content.append(table_sql)
        
        main_sql_file = os.path.join(output_dir, f"{design.name}_tables.sql")
        with open(main_sql_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(main_sql_content))
        generated_files.append(main_sql_file)
        logger.info(f"Generated main SQL file: {main_sql_file}")
        
        # 也可以为每个表生成单独的SQL文件（可选）
        for table in design.tables:
            table_sql = self.sql_generator.generate_create_table_sql(table)
            table_file = os.path.join(output_dir, f"{self._to_snake_case(table.name)}.sql")
            with open(table_file, 'w', encoding='utf-8') as f:
                f.write(table_sql)
            generated_files.append(table_file)
            logger.info(f"Generated table SQL file: {table_file}")
        
        return generated_files
    
    def _generate_separate_orm_files(self, design: DatabaseDesign, output_dir: str) -> List[str]:
        """生成分离的ORM文件"""
        generated_files = []
        
        for table in design.tables:
            # 生成单个表的ORM文件
            content_parts = [
                "#!/usr/bin/env python3",
                '"""',
                f"Generated ORM model for {table.name}",
                f"Generated at: {datetime.now().isoformat()}",
                '"""',
                "",
                "from pyadvincekit.models.base import (",
                "    BaseModel, create_required_string_column, create_decimal_column,",
                "    create_uuid_column, create_float_column, create_bigint_column,",
                "    create_enum_column, create_date_column, create_time_column,",
                "    create_binary_column, create_email_column, create_phone_column,",
                "    create_url_column, create_status_column, create_sort_order_column,",
                "    create_foreign_key_column, create_version_column",
                ")",
                "from datetime import datetime, date, time",
                "from typing import Optional",
                "from sqlalchemy.orm import Mapped",
                "",
                ""
            ]
            
            # 生成ORM模型
            model_content = self.orm_generator.generate_model(table)
            content_parts.append(model_content)
            
            # 写入文件
            filename = f"{self._to_snake_case(table.name)}.py"
            file_path = os.path.join(output_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(content_parts))
            
            generated_files.append(file_path)
            logger.info(f"Generated ORM file: {file_path}")
        
        return generated_files
    
    def _generate_separate_schema_files(self, design: DatabaseDesign, output_dir: str) -> List[str]:
        """生成分离的Schema文件"""
        generated_files = []
        
        for table in design.tables:
            # 生成单个表的Schema文件
            content_parts = [
                "#!/usr/bin/env python3",
                '"""',
                f"Generated Pydantic schemas for {table.name}",
                f"Generated at: {datetime.now().isoformat()}",
                '"""',
                "",
                "from pydantic import BaseModel, Field",
                "from datetime import datetime, date, time",
                "from typing import Optional, Any, List",
                "from decimal import Decimal",
                "",
                ""
            ]
            
            # 生成Pydantic模式
            schema_content = self.pydantic_generator.generate_schema(table)
            content_parts.append(schema_content)
            
            # 写入文件
            filename = f"{self._to_snake_case(table.name)}.py"
            file_path = os.path.join(output_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(content_parts))
            
            generated_files.append(file_path)
            logger.info(f"Generated Schema file: {file_path}")
        
        return generated_files
    
    def _generate_orm_init_file(self, design: DatabaseDesign, output_dir: str) -> str:
        """生成ORM模块的__init__.py文件"""
        content_parts = [
            "#!/usr/bin/env python3",
            '"""',
            f"ORM Models for {design.name}",
            f"Generated at: {datetime.now().isoformat()}",
            '"""',
            "",
            "# Import all models",
        ]
        
        # 导入所有模型
        for table in design.tables:
            snake_name = self._to_snake_case(table.name)
            class_name = self._to_pascal_case(table.name)
            content_parts.append(f"from .{snake_name} import {class_name}")
        
        content_parts.extend([
            "",
            "# Export all models",
            "__all__ = ["
        ])
        
        # 导出列表
        for table in design.tables:
            class_name = self._to_pascal_case(table.name)
            content_parts.append(f'    "{class_name}",')
        
        content_parts.append("]")
        
        # 写入文件
        init_file = os.path.join(output_dir, "__init__.py")
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(content_parts))
        
        logger.info(f"Generated ORM __init__.py file: {init_file}")
        return init_file
    
    def _generate_schema_init_file(self, design: DatabaseDesign, output_dir: str) -> str:
        """生成Schema模块的__init__.py文件"""
        content_parts = [
            "#!/usr/bin/env python3",
            '"""',
            f"Pydantic Schemas for {design.name}",
            f"Generated at: {datetime.now().isoformat()}",
            '"""',
            "",
            "# Import all schemas",
        ]
        
        # 导入所有schema
        for table in design.tables:
            snake_name = self._to_snake_case(table.name)
            base_name = self._to_pascal_case(table.name)
            content_parts.extend([
                f"from .{snake_name} import (",
                f"    {base_name}Base, {base_name}Create, {base_name}Update,",
                f"    {base_name}Response, {base_name}InDB, {base_name}Query, {base_name}Filter",
                ")"
            ])
        
        content_parts.extend([
            "",
            "# Export all schemas",
            "__all__ = ["
        ])
        
        # 导出列表
        for table in design.tables:
            base_name = self._to_pascal_case(table.name)
            content_parts.extend([
                f'    "{base_name}Base",',
                f'    "{base_name}Create",',
                f'    "{base_name}Update",',
                f'    "{base_name}Response",',
                f'    "{base_name}InDB",',
                f'    "{base_name}Query",',
                f'    "{base_name}Filter",',
            ])
        
        content_parts.append("]")
        
        # 写入文件
        init_file = os.path.join(output_dir, "__init__.py")
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(content_parts))
        
        logger.info(f"Generated Schema __init__.py file: {init_file}")
        return init_file
    
    def _to_snake_case(self, name: str) -> str:
        """将表名转换为snake_case"""
        # 处理驼峰命名
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _to_pascal_case(self, name: str) -> str:
        """将表名转换为PascalCase"""
        # 处理下划线分隔的名称
        parts = name.replace('-', '_').split('_')
        return ''.join(word.capitalize() for word in parts if word)


# 便捷函数
def generate_database_code(
    excel_file: str,
    output_dir: str = "generated",
    generate_sql: bool = True,
    generate_orm: bool = True,
    generate_pydantic: bool = True,
    database_name: Optional[str] = None,
    # 新增参数：支持分目录和分文件生成
    orm_output_dir: Optional[str] = None,
    schema_output_dir: Optional[str] = None,
    sql_output_dir: Optional[str] = None,
    separate_files: bool = False,
    auto_init_files: bool = True,
    # 🔥 新增参数：是否自动添加标准字段
    add_standard_fields: bool = True
) -> Dict[str, Any]:
    """
    生成数据库代码的便捷函数
    
    Args:
        excel_file: Excel文件路径
        output_dir: 默认输出目录
        generate_sql: 是否生成SQL
        generate_orm: 是否生成ORM
        generate_pydantic: 是否生成Pydantic
        database_name: 数据库名称
        orm_output_dir: ORM文件输出目录（如果不指定则使用output_dir）
        schema_output_dir: Schema文件输出目录（如果不指定则使用output_dir）
        sql_output_dir: SQL文件输出目录（如果不指定则使用output_dir）
        separate_files: 是否按表分别生成文件
        auto_init_files: 是否自动生成__init__.py文件
        add_standard_fields: 是否自动为每个表添加标准字段（id, created_at, updated_at）
    
    Returns:
        生成文件信息的字典
    """
    generator = DatabaseCodeGenerator(add_standard_fields=add_standard_fields)
    
    if separate_files:
        # 使用新的分文件生成方法
        return generator.generate_separate_files(
            excel_file=excel_file,
            output_dir=output_dir,
            orm_output_dir=orm_output_dir,
            schema_output_dir=schema_output_dir,
            sql_output_dir=sql_output_dir,
            generate_sql=generate_sql,
            generate_orm=generate_orm,
            generate_pydantic=generate_pydantic,
            database_name=database_name,
            auto_init_files=auto_init_files
        )
    else:
        # 使用原有的单文件生成方法
        return generator.generate_from_excel(
            excel_file=excel_file,
            output_dir=output_dir,
            generate_sql=generate_sql,
            generate_orm=generate_orm,
            generate_pydantic=generate_pydantic,
            database_name=database_name
        )


def generate_sql_from_excel(excel_file: str, output_file: str) -> str:
    """从Excel生成SQL的便捷函数"""
    generator = DatabaseCodeGenerator()
    return generator.generate_sql_only(excel_file, output_file)


def generate_orm_from_excel(excel_file: str, output_file: str) -> str:
    """从Excel生成ORM的便捷函数"""
    generator = DatabaseCodeGenerator()
    return generator.generate_orm_only(excel_file, output_file)


def generate_pydantic_from_excel(excel_file: str, output_file: str) -> str:
    """从Excel生成Pydantic的便捷函数"""
    generator = DatabaseCodeGenerator()
    return generator.generate_pydantic_only(excel_file, output_file)

