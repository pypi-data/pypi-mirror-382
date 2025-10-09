#!/usr/bin/env python3
"""
数据库逆向生成器

提供从数据库连接逆向生成ORM和Schema对象的API
"""

from typing import Dict, List, Optional, Any

from pyadvincekit.logging import get_logger
from pyadvincekit.core.database_extractor import DatabaseMetadataExtractor
from pyadvincekit.core.code_generator import DatabaseCodeGenerator

logger = get_logger(__name__)


async def generate_from_database(
    database_url: Optional[str] = None,
    database_name: Optional[str] = None,
    output_dir: str = "generated_from_db",
    
    # 复用现有选项
    orm_output_dir: Optional[str] = None,
    schema_output_dir: Optional[str] = None,
    sql_output_dir: Optional[str] = None,
    separate_files: bool = False,
    auto_init_files: bool = True,
    
    # 过滤选项
    include_tables: Optional[List[str]] = None,
    exclude_tables: Optional[List[str]] = None,
    table_prefix: Optional[str] = None,
    
    # 生成选项
    generate_sql: bool = True,
    generate_orm: bool = True,
    generate_pydantic: bool = True
) -> Dict[str, Any]:
    """
    从数据库逆向生成代码
    
    Args:
        database_url: 可选的数据库连接URL，如果不提供则使用PyAdvanceKit配置
        database_name: 数据库名称
        output_dir: 输出目录
        orm_output_dir: ORM文件输出目录
        schema_output_dir: Schema文件输出目录
        sql_output_dir: SQL文件输出目录
        separate_files: 是否按表分别生成文件
        auto_init_files: 是否自动生成__init__.py文件
        include_tables: 指定要生成的表列表
        exclude_tables: 排除的表列表
        table_prefix: 表名前缀过滤
        generate_sql: 是否生成SQL
        generate_orm: 是否生成ORM
        generate_pydantic: 是否生成Pydantic
    
    Returns:
        生成文件信息的字典
    """
    
    logger.info(f"Starting database reverse generation")
    logger.info(f"Database URL: {'<configured>' if not database_url else database_url}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Separate files: {separate_files}")
    
    # 1. 创建元数据提取器（使用PyAdvanceKit的数据库管理器）
    extractor = DatabaseMetadataExtractor(database_url)
    
    # 2. 提取数据库设计
    design = await extractor.extract_database_design(database_name)
    
    logger.info(f"Extracted {len(design.tables)} tables from database")
    
    # 3. 过滤表
    original_table_count = len(design.tables)
    
    if include_tables:
        design.tables = [t for t in design.tables if t.name in include_tables]
        logger.info(f"Filtered by include_tables: {len(design.tables)} tables remaining")
    
    if exclude_tables:
        design.tables = [t for t in design.tables if t.name not in exclude_tables]
        logger.info(f"Filtered by exclude_tables: {len(design.tables)} tables remaining")
    
    if table_prefix:
        design.tables = [t for t in design.tables if t.name.startswith(table_prefix)]
        logger.info(f"Filtered by table_prefix '{table_prefix}': {len(design.tables)} tables remaining")
    
    if len(design.tables) != original_table_count:
        filtered_table_names = [t.name for t in design.tables]
        logger.info(f"Final table list: {filtered_table_names}")
    
    if not design.tables:
        logger.warning("No tables found after filtering, nothing to generate")
        return {
            "orm_files": [],
            "schema_files": [],
            "sql_files": [],
            "init_files": []
        }
    
    # 4. 使用现有的代码生成器
    generator = DatabaseCodeGenerator()
    
    if separate_files:
        logger.info("Using separate files generation mode")
        return generator.generate_separate_files_from_design(
            design=design,
            output_dir=output_dir,
            orm_output_dir=orm_output_dir,
            schema_output_dir=schema_output_dir,
            sql_output_dir=sql_output_dir,
            generate_sql=generate_sql,
            generate_orm=generate_orm,
            generate_pydantic=generate_pydantic,
            auto_init_files=auto_init_files
        )
    else:
        logger.info("Using single file generation mode")
        return generator.generate_from_design(
            design=design,
            output_dir=output_dir,
            generate_sql=generate_sql,
            generate_orm=generate_orm,
            generate_pydantic=generate_pydantic
        )


# 便捷函数
async def generate_models_from_database(
    database_url: Optional[str] = None,
    output_dir: str = "generated_models",
    include_tables: Optional[List[str]] = None,
    exclude_tables: Optional[List[str]] = None,
    separate_files: bool = True
) -> Dict[str, Any]:
    """
    从数据库生成ORM模型的便捷函数
    
    Args:
        database_url: 数据库连接URL
        output_dir: 输出目录
        include_tables: 包含的表
        exclude_tables: 排除的表
        separate_files: 是否分文件生成
    
    Returns:
        生成文件信息
    """
    return await generate_from_database(
        database_url=database_url,
        output_dir=output_dir,
        include_tables=include_tables,
        exclude_tables=exclude_tables,
        separate_files=separate_files,
        generate_sql=False,
        generate_orm=True,
        generate_pydantic=False
    )


async def generate_schemas_from_database(
    database_url: Optional[str] = None,
    output_dir: str = "generated_schemas",
    include_tables: Optional[List[str]] = None,
    exclude_tables: Optional[List[str]] = None,
    separate_files: bool = True
) -> Dict[str, Any]:
    """
    从数据库生成Pydantic Schema的便捷函数
    
    Args:
        database_url: 数据库连接URL
        output_dir: 输出目录
        include_tables: 包含的表
        exclude_tables: 排除的表
        separate_files: 是否分文件生成
    
    Returns:
        生成文件信息
    """
    return await generate_from_database(
        database_url=database_url,
        output_dir=output_dir,
        include_tables=include_tables,
        exclude_tables=exclude_tables,
        separate_files=separate_files,
        generate_sql=False,
        generate_orm=False,
        generate_pydantic=True
    )


async def generate_all_from_database(
    database_url: Optional[str] = None,
    project_dir: str = "generated_project",
    include_tables: Optional[List[str]] = None,
    exclude_tables: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    从数据库生成完整项目结构的便捷函数
    
    Args:
        database_url: 数据库连接URL
        project_dir: 项目目录
        include_tables: 包含的表
        exclude_tables: 排除的表
    
    Returns:
        生成文件信息
    """
    return await generate_from_database(
        database_url=database_url,
        output_dir=project_dir,
        orm_output_dir=f"{project_dir}/models",
        schema_output_dir=f"{project_dir}/schemas",
        sql_output_dir=f"{project_dir}/sql",
        include_tables=include_tables,
        exclude_tables=exclude_tables,
        separate_files=True,
        auto_init_files=True,
        generate_sql=True,
        generate_orm=True,
        generate_pydantic=True
    )








