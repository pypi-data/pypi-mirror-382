#!/usr/bin/env python3
"""
使用示例：展示如何使用pyadvincekit的Excel数据库设计生成功能
excel 转 sql ，sql转ORM scheme 对象

"""

from pyadvincekit import (
    # 统一代码生成器
    generate_database_code, generate_sql_from_excel, generate_orm_from_excel, generate_pydantic_from_excel,
    
    # 数据库设计解析器
    parse_database_design_excel, DatabaseDesignParser,
    
    # 基础组件
    DatabaseCodeGenerator
)


def example_unified_generation():
    """示例1：使用统一代码生成器生成所有代码"""
    print("🎯 示例1：统一代码生成")
    print("=" * 50)
    
    excel_file = "../data2.xlsx"
    output_dir = "generated_code"
    
    # 生成所有代码（SQL、ORM、Pydantic）
    generated_files = generate_database_code(
        excel_file=excel_file,
        output_dir=output_dir,
        generate_sql=True,
        generate_orm=True,
        generate_pydantic=True,
        database_name="my_database"  # 可选：指定数据库名称
    )
    
    print("✅ 生成完成！")
    for file_type, file_path in generated_files.items():
        print(f"   - {file_type}: {file_path}")


def example_individual_generation():
    """示例2：分别生成不同类型的代码"""
    print("\n🎯 示例2：分别生成代码")
    print("=" * 50)
    
    excel_file = "../data2.xlsx"
    
    # 只生成SQL
    sql_content = generate_sql_from_excel(excel_file, "database.sql")
    print(f"✅ SQL已生成: database.sql")
    
    # 只生成ORM
    orm_content = generate_orm_from_excel(excel_file, "../models.py")
    print(f"✅ ORM已生成: models.py")
    
    # 只生成Pydantic
    pydantic_content = generate_pydantic_from_excel(excel_file, "../schemas.py")
    print(f"✅ Pydantic已生成: schemas.py")


def example_parser_usage():
    """示例3：使用解析器获取数据库设计信息"""
    print("\n🎯 示例3：解析数据库设计")
    print("=" * 50)
    
    excel_file = "../data2.xlsx"
    
    # 解析Excel文件
    design = parse_database_design_excel(excel_file)
    
    print(f"📊 数据库信息:")
    print(f"   名称: {design.name}")
    print(f"   版本: {design.version}")
    print(f"   描述: {design.description}")
    print(f"   表数量: {len(design.tables)}")
    
    for table in design.tables:
        print(f"\n📋 表: {table.name}")
        print(f"   描述: {table.comment}")
        print(f"   列数: {len(table.columns)}")
        print(f"   索引数: {len(table.indexes)}")
        
        for column in table.columns:
            constraints_str = ", ".join([c.type.value for c in column.constraints])
            print(f"   - {column.name}: {column.get_sql_type()} ({constraints_str}) - {column.comment}")


def example_advanced_usage():
    """示例4：高级用法 - 自定义生成器"""
    print("\n🎯 示例4：高级用法")
    print("=" * 50)
    
    # 创建自定义生成器
    generator = DatabaseCodeGenerator()
    
    excel_file = "../data2.xlsx"
    
    # 自定义生成
    generated_files = generator.generate_from_excel(
        excel_file=excel_file,
        output_dir="custom_output",
        generate_sql=True,
        generate_orm=False,  # 不生成ORM
        generate_pydantic=True,
        database_name="custom_db"
    )
    
    print("✅ 自定义生成完成！")
    for file_type, file_path in generated_files.items():
        print(f"   - {file_type}: {file_path}")


def example_parser_only():
    """示例5：只使用解析器，不生成代码"""
    print("\n🎯 示例5：只解析设计")
    print("=" * 50)
    
    # 创建解析器
    parser = DatabaseDesignParser()
    
    excel_file = "../data2.xlsx"
    
    # 解析Excel文件
    design = parser.parse_excel_file(excel_file)
    
    # 可以在这里进行自定义处理
    print(f"📊 解析到 {len(design.tables)} 个表")
    
    # 例如：只处理特定类型的表
    for table in design.tables:
        if "user" in table.name.lower():
            print(f"🔍 找到用户相关表: {table.name}")
            # 进行特殊处理...


if __name__ == "__main__":
    print("🚀 PyAdvanceKit Excel数据库设计生成功能使用示例")
    print("=" * 60)
    
    try:
        # 运行所有示例
        example_unified_generation()
        example_individual_generation()
        example_parser_usage()
        example_advanced_usage()
        example_parser_only()
        
        print("\n🎉 所有示例运行完成！")
        
    except Exception as e:
        print(f"\n❌ 示例运行失败: {e}")
        import traceback
        traceback.print_exc()
