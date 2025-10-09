"""
阶段二：数据库操作示例

演示 PyAdvanceKit 的数据库功能：
- 数据库模型定义
- CRUD操作
- 查询和过滤
- 软删除
- 批量操作
- 数据库连接管理
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from sqlalchemy import String, Integer, Float, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置 .env 文件路径
env_file = Path(__file__).parent / ".env"
# 如果 .env 不存在，尝试使用 my_config.env
# 如果 .env 不存在，尝试使用 my_config.env
if not env_file.exists():
    env_file = Path(__file__).parent / "my_config.env"
if env_file.exists():
    print(f"📁 发现配置文件: {env_file}")
    # 手动设置环境变量，确保 .env 文件被加载
    import os
    try:
        from dotenv import load_dotenv
        # 指定编码为 utf-8
        load_dotenv(env_file, encoding='utf-8')
        print("✅ 已加载 .env 配置文件")
    except ImportError:
        print("⚠️ 未安装 python-dotenv，使用系统环境变量")
        print("   安装命令: pip install python-dotenv")
    except Exception as e:
        print(f"⚠️ 加载 .env 文件失败: {e}")
        print("   请检查文件编码是否为 UTF-8")
else:
    print("💡 提示: 可以在 examples 目录下创建 .env 文件来配置数据库连接")
    print("   参考: examples/env_template.txt")

from pyadvincekit import (
    BaseModel, SoftDeleteModel, BaseCRUD, 
    get_database, init_database
)
from pyadvincekit.core import reset_database_manager, set_database_manager
from pyadvincekit.core.config import get_settings, reload_settings
from pyadvincekit.core.database import DatabaseManager

from pyadvincekit.models.base import (
    create_required_string_column, create_text_column
)
# 导入配置相关模块
from pyadvincekit.core.config import Settings
from pyadvincekit.core.database import DatabaseManager



# ================== 模型定义示例 ==================

class User(BaseModel):
    """用户模型 - 使用BaseModel"""
    __tablename__ = "users"
    
    # 使用便捷字段函数
    name: Mapped[str] = create_required_string_column(100, comment="用户姓名")
    email: Mapped[str] = create_required_string_column(255, unique=True, comment="邮箱地址")
    age: Mapped[int] = mapped_column(Integer, nullable=True, comment="年龄")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")


class Product(SoftDeleteModel):
    """产品模型 - 使用SoftDeleteModel支持软删除"""
    __tablename__ = "products"
    
    name: Mapped[str] = create_required_string_column(200, comment="产品名称")
    description: Mapped[str] = create_text_column(comment="产品描述")
    price: Mapped[float] = mapped_column(Float, nullable=False, comment="价格")
    stock: Mapped[int] = mapped_column(Integer, default=0, comment="库存数量")


class Order(BaseModel):
    """订单模型"""
    __tablename__ = "orders"
    
    order_no: Mapped[str] = create_required_string_column(50, unique=True, comment="订单号")
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, comment="用户ID")
    product_id: Mapped[str] = mapped_column(String(36), nullable=False, comment="产品ID")
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, comment="数量")
    total_price: Mapped[float] = mapped_column(Float, nullable=False, comment="总价")


# ================== CRUD操作示例 ==================

async def example_basic_crud():
    """基础CRUD操作示例"""
    print("=== 基础CRUD操作示例 ===")
    
    # 创建CRUD实例
    user_crud = BaseCRUD(User)
    
    async with get_database() as db:
        # 1. 创建用户
        print("1. 创建用户")
        user_data = {
            "name": "张三",
            "email": "zhangsan@example.com",
            "age": 25,
            "is_active": True
        }
        user = await user_crud.create(db, user_data)
        print(f"   创建成功: ID={user.id}, 姓名={user.name}")
        
        # 2. 获取用户
        print("2. 获取用户")
        retrieved_user = await user_crud.get(db, user.id)
        print(f"   查询成功: {retrieved_user.name} ({retrieved_user.email})")
        
        # 3. 更新用户
        print("3. 更新用户")
        update_data = {"name": "李四", "age": 30}
        updated_user = await user_crud.update(db, retrieved_user, update_data)
        print(f"   更新成功: 新姓名={updated_user.name}, 新年龄={updated_user.age}")
        
        # 4. 检查存在性
        print("4. 检查存在性")
        exists = await user_crud.exists(db, user.id)
        print(f"   用户存在: {exists}")
        
        # 5. 删除用户
        print("5. 删除用户")
        success = await user_crud.delete(db, user.id)
        print(f"   删除成功: {success}")
        
        # 验证删除
        exists_after = await user_crud.exists(db, user.id)
        print(f"   删除后存在: {exists_after}")
    
    print()


async def example_query_operations():
    """查询操作示例"""
    print("=== 查询操作示例 ===")
    
    user_crud = BaseCRUD(User)

    async with get_database() as db:
        # 先清理已存在的测试数据
        print("0. 清理已存在的测试数据")
        existing_users = await user_crud.get_multi(db, limit=100)
        for user in existing_users:
            await user_crud.delete(db, user.id)
        print(f"   清理了 {len(existing_users)} 个已存在的用户")

    async with get_database() as db:
        # 先创建一些测试数据
        print("1. 创建测试数据")
        users_data = [
            {"name": "Alice", "email": "alice@example.com", "age": 25, "is_active": True},
            {"name": "Bob", "email": "bob@example.com", "age": 30, "is_active": True},
            {"name": "Charlie", "email": "charlie@example.com", "age": 35, "is_active": False},
            {"name": "David", "email": "david@example.com", "age": 28, "is_active": True},
            {"name": "Eva", "email": "eva@example.com", "age": 32, "is_active": True},
        ]
        created_users = await user_crud.bulk_create(db, users_data)
        print(f"   批量创建了 {len(created_users)} 个用户")
        
        # 2. 获取所有用户
        print("2. 获取所有用户")
        all_users = await user_crud.get_multi(db, limit=10)
        print(f"   总用户数: {len(all_users)}")
        for user in all_users:
            print(f"   - {user.name} ({user.age}岁, {'激活' if user.is_active else '未激活'})")
        
        # 3. 分页查询
        print("3. 分页查询")
        page1 = await user_crud.get_multi(db, skip=0, limit=2)
        page2 = await user_crud.get_multi(db, skip=2, limit=2)
        print(f"   第1页: {[u.name for u in page1]}")
        print(f"   第2页: {[u.name for u in page2]}")
        
        # 4. 排序查询
        print("4. 排序查询")
        users_by_age = await user_crud.get_multi(db, order_by="age", order_desc=True)
        print("   按年龄降序:")
        for user in users_by_age:
            print(f"   - {user.name}: {user.age}岁")
        
        # 5. 过滤查询
        print("5. 过滤查询")
        
        # 简单过滤
        active_users = await user_crud.get_multi(db, filters={"is_active": True})
        print(f"   激活用户: {[u.name for u in active_users]}")
        
        # 复杂过滤
        young_users = await user_crud.get_multi(
            db, 
            filters={"age": {"operator": "lt", "value": 30}}
        )
        print(f"   30岁以下用户: {[u.name for u in young_users]}")
        
        # 模糊查询
        a_users = await user_crud.get_multi(
            db,
            filters={"name": {"operator": "like", "value": "A"}}
        )
        print(f"   姓名包含'A'的用户: {[u.name for u in a_users]}")
        
        # 列表过滤
        selected_users = await user_crud.get_multi(
            db,
            filters={"name": ["Alice", "Bob"]}
        )
        print(f"   指定姓名用户: {[u.name for u in selected_users]}")
        
        # 6. 计数
        print("6. 计数操作")
        total_count = await user_crud.count(db)
        active_count = await user_crud.count(db, filters={"is_active": True})
        print(f"   总用户数: {total_count}")
        print(f"   激活用户数: {active_count}")
    
    print()


async def example_soft_delete():
    """软删除示例"""
    print("=== 软删除示例 ===")
    
    product_crud = BaseCRUD(Product)
    
    async with get_database() as db:
        # 1. 创建产品
        print("1. 创建产品")
        products_data = [
            {"name": "iPhone 15", "description": "最新款iPhone", "price": 7999.0, "stock": 100},
            {"name": "MacBook Pro", "description": "专业笔记本", "price": 15999.0, "stock": 50},
            {"name": "iPad Air", "description": "轻薄平板", "price": 4599.0, "stock": 80},
        ]
        products = await product_crud.bulk_create(db, products_data)
        print(f"   创建了 {len(products)} 个产品")
        
        # 2. 查看所有产品
        print("2. 查看所有产品")
        all_products = await product_crud.get_multi(db)
        for product in all_products:
            print(f"   - {product.name}: ¥{product.price} (库存: {product.stock})")
        
        # 3. 软删除产品
        print("3. 软删除产品")
        iphone = products[0]
        deleted_product = await product_crud.soft_delete(db, iphone.id)
        print(f"   软删除产品: {deleted_product.name}")
        print(f"   删除状态: is_deleted={deleted_product.is_deleted}")
        print(f"   删除时间: {deleted_product.deleted_at}")
        
        # 4. 默认查询（不包含已删除）
        print("4. 默认查询（不包含已删除）")
        active_products = await product_crud.get_multi(db)
        print(f"   活跃产品数: {len(active_products)}")
        for product in active_products:
            print(f"   - {product.name}")
        
        # 5. 包含已删除的查询
        print("5. 包含已删除的查询")
        all_products_with_deleted = await product_crud.get_multi(db, include_deleted=True)
        print(f"   总产品数: {len(all_products_with_deleted)}")
        for product in all_products_with_deleted:
            status = "已删除" if product.is_deleted else "正常"
            print(f"   - {product.name} ({status})")
        
        # 6. 恢复产品
        print("6. 恢复产品")
        restored_product = await product_crud.restore(db, iphone.id)
        print(f"   恢复产品: {restored_product.name}")
        print(f"   删除状态: is_deleted={restored_product.is_deleted}")
        print(f"   删除时间: {restored_product.deleted_at}")
        
        # 7. 验证恢复
        print("7. 验证恢复")
        final_products = await product_crud.get_multi(db)
        print(f"   最终产品数: {len(final_products)}")
    
    print()


async def example_model_methods():
    """模型方法示例"""
    print("=== 模型方法示例 ===")
    
    async with get_database() as db:
        # 1. 从字典创建模型
        print("1. 从字典创建模型")
        user_data = {
            "name": "测试用户",
            "email": "test@example.com",
            "age": 25,
            "is_active": True
        }
        user = User.from_dict(user_data)
        print(f"   从字典创建: {user.name}")
        
        # 保存到数据库
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # 2. 转换为字典
        print("2. 转换为字典")
        user_dict = user.to_dict()
        print("   完整字典:")
        for key, value in user_dict.items():
            print(f"     {key}: {value}")
        
        # 排除某些字段
        user_dict_no_timestamps = user.to_dict(exclude=["created_at", "updated_at"])
        print("   排除时间戳:")
        for key, value in user_dict_no_timestamps.items():
            print(f"     {key}: {value}")
        
        # 3. 从字典更新
        print("3. 从字典更新")
        update_data = {"name": "更新后的用户", "age": 30}
        user.update_from_dict(update_data)
        await db.commit()
        await db.refresh(user)
        print(f"   更新后: {user.name}, 年龄: {user.age}")
        
        # 4. 模型字符串表示
        print("4. 模型字符串表示")
        print(f"   __repr__: {repr(user)}")
        print(f"   __str__: {str(user)}")
    
    print()


async def example_complex_operations():
    """复杂操作示例"""
    print("=== 复杂操作示例 ===")
    
    user_crud = BaseCRUD(User)
    product_crud = BaseCRUD(Product)
    order_crud = BaseCRUD(Order)
    
    async with get_database() as db:
        # 1. 创建用户和产品
        print("1. 创建用户和产品")
        user = await user_crud.create(db, {
            "name": "购买者",
            "email": "buyer@example.com",
            "age": 28
        })
        
        product = await product_crud.create(db, {
            "name": "MacBook Pro",
            "description": "专业笔记本电脑", 
            "price": 15999.0,
            "stock": 10
        })
        
        print(f"   用户: {user.name} (ID: {user.id})")
        print(f"   产品: {product.name} (ID: {product.id})")
        
        # 2. 创建订单
        print("2. 创建订单")
        order_data = {
            "order_no": f"ORDER-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_id": user.id,
            "product_id": product.id,
            "quantity": 2,
            "total_price": product.price * 2
        }
        order = await order_crud.create(db, order_data)
        print(f"   订单: {order.order_no}, 总价: ¥{order.total_price}")
        
        # 3. 查询用户的所有订单
        print("3. 查询用户的所有订单")
        user_orders = await order_crud.get_multi(db, filters={"user_id": user.id})
        print(f"   用户订单数: {len(user_orders)}")
        for ord in user_orders:
            print(f"   - {ord.order_no}: 数量{ord.quantity}, 总价¥{ord.total_price}")
        
        # 4. 批量操作
        print("4. 批量操作")
        # 批量创建更多订单
        more_orders = []
        import uuid
        for i in range(3):
            more_orders.append({
                "order_no": f"ORDER-BATCH-{uuid.uuid4().hex[:8]}-{i + 1:03d}",
                "user_id": user.id,
                "product_id": product.id,
                "quantity": 1,
                "total_price": product.price
            })
        
        batch_orders = await order_crud.bulk_create(db, more_orders)
        print(f"   批量创建了 {len(batch_orders)} 个订单")
        
        # 5. 统计信息
        print("5. 统计信息")
        total_orders = await order_crud.count(db)
        user_total_orders = await order_crud.count(db, filters={"user_id": user.id})
        
        print(f"   总订单数: {total_orders}")
        print(f"   该用户订单数: {user_total_orders}")
        
        # 6. 复杂查询
        print("6. 复杂查询")
        # 查询金额大于15000的订单
        expensive_orders = await order_crud.get_multi(
            db,
            filters={"total_price": {"operator": "gt", "value": 15000}},
            order_by="total_price",
            order_desc=True
        )
        print(f"   高价订单数: {len(expensive_orders)}")
        for ord in expensive_orders:
            print(f"   - {ord.order_no}: ¥{ord.total_price}")
    
    print()


async def main():
    """主函数"""
    print("🚀 PyAdvanceKit 数据库操作示例")
    print("=" * 50)

    # settings = Settings(
    #     database={
    #         # "database_url": "sqlite:///./x_app1.db",
    #         "database_url": "mysql+aiomysql://root:123456@localhost/a_database",
    #         "echo_sql": True,
    #         "pool_size": 5
    #     },
    #     environment="development",
    #     debug=True
    # )

    # 使用自定义配置创建数据库管理器
    # db_manager = DatabaseManager(settings)
    # print("✅ 已创建自定义数据库管理器")
    # set_database_manager(db_manager)
    # 初始化数据库
    print("📊 初始化数据库...")
    await init_database()
    print("✅ 数据库初始化完成")
    print()
    
    # 运行所有示例
    await example_basic_crud()
    await example_query_operations() 
    await example_soft_delete()
    await example_model_methods()
    await example_complex_operations()
    
    print("✅ 数据库操作示例完成！")
    print("\n💡 提示:")
    print("1. 所有操作都是异步的，性能更好")
    print("2. CRUD操作自动处理异常和事务")
    print("3. 支持软删除，数据更安全")
    print("4. 查询功能丰富，支持过滤、排序、分页")
    print("5. 模型有便捷的字典转换方法")


if __name__ == "__main__":
    asyncio.run(main())
