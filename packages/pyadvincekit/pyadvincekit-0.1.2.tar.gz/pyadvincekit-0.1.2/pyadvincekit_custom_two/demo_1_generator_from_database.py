from pyadvincekit import generate_database_code
import asyncio

"""
    1.演示 从Excel 生成 ORM对象，schemas对象 ，sql 文件
    2.演示 从 database 生成 ORM对象，schemas对象
"""
async def database_reverse_generation():
    from pyadvincekit import (
        generate_from_database,
        generate_models_from_database,
        generate_schemas_from_database,
        generate_all_from_database,
        get_logger
    )
    result = await generate_from_database(
                    output_dir="./generator_from_database/",
                    separate_files=True,
                    auto_init_files=True,
                    generate_sql=False,
                    generate_orm=True,
                    generate_pydantic=True
                )

if __name__ == '__main__':
    # 1. 一行代码实现 从Excel 中生成 ORM 对象和schemas对象
    result = generate_database_code(
        excel_file="database_design.xls",

        # 指定各自的输出目录
        orm_output_dir="models",  # ORM对象放到models文件夹
        schema_output_dir="schemas",  # Schema对象放到schemas文件夹
        sql_output_dir="sql",  # SQL文件放到sql文件夹

        # 每个表生成一个文件
        separate_files=True,

        # 自动生成__init__.py
        auto_init_files=True,
        add_standard_fields = True  # 启用
    )

    # 2 . 实现读取 database 数据库,生成 ORM 对象和schemas对象
    # exit_code = asyncio.run(database_reverse_generation())