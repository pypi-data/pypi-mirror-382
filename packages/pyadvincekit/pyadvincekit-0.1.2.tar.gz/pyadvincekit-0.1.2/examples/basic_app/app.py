"""
基础应用完整示例

一个使用 PyAdvanceKit 构建的完整示例应用，包含：
- 用户管理
- 产品管理
- 配置管理
- 数据库操作
- 错误处理

这个示例展示了如何用最少的代码实现一个功能完整的应用。
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional
from sqlalchemy import String, Integer, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pyadvincekit import (
    Settings, BaseModel, SoftDeleteModel, BaseCRUD,
    get_database, init_database
)
from pyadvincekit.models.base import (
    create_required_string_column, create_text_column
)
from pyadvincekit.core.exceptions import RecordNotFoundError, ValidationError


# ================== 配置设置 ==================

# 应用配置
app_settings = Settings(
    app_name="PyAdvanceKit 示例应用",
    environment="development",
    debug=True,
    database={
        "database_url": "sqlite+aiosqlite:///./example_app1.db",
        "echo_sql": True,  # 开发环境显示SQL
    },
    logging={
        "log_level": "INFO",
        "log_file_enabled": True,
        "log_file_path": "logs/example_app.log"
    }
)


# ================== 数据模型 ==================

class User(BaseModel):
    """用户模型"""
    __tablename__ = "users"
    
    username: Mapped[str] = create_required_string_column(50, unique=True, comment="用户名")
    email: Mapped[str] = create_required_string_column(255, unique=True, comment="邮箱")
    full_name: Mapped[str] = create_required_string_column(100, comment="全名")
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="年龄")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")


class Product(SoftDeleteModel):
    """产品模型（支持软删除）"""
    __tablename__ = "products"
    
    name: Mapped[str] = create_required_string_column(200, comment="产品名称")
    description: Mapped[Optional[str]] = create_text_column(comment="产品描述")
    price: Mapped[float] = mapped_column(Float, nullable=False, comment="价格")
    stock: Mapped[int] = mapped_column(Integer, default=0, comment="库存")
    category: Mapped[str] = create_required_string_column(100, comment="分类")


# ================== 业务逻辑层 ==================

class UserService:
    """用户服务"""
    
    def __init__(self):
        self.crud = BaseCRUD(User)
    
    async def create_user(self, user_data: dict) -> User:
        """创建用户"""
        # 数据验证
        if not user_data.get("username"):
            raise ValidationError("用户名不能为空", field="username")
        
        if not user_data.get("email"):
            raise ValidationError("邮箱不能为空", field="email")
        
        # 检查邮箱格式
        email = user_data["email"]
        if "@" not in email:
            raise ValidationError("邮箱格式不正确", field="email", value=email)
        
        async with get_database() as db:
            # 检查用户名和邮箱是否已存在
            existing_users = await self.crud.get_multi(
                db, 
                filters={"username": user_data["username"]}
            )
            if existing_users:
                raise ValidationError("用户名已存在", field="username")
            
            existing_emails = await self.crud.get_multi(
                db,
                filters={"email": user_data["email"]}
            )
            if existing_emails:
                raise ValidationError("邮箱已被使用", field="email")
            
            # 创建用户
            return await self.crud.create(db, user_data)
    
    async def get_user(self, user_id: str) -> User:
        """获取用户"""
        async with get_database() as db:
            return await self.crud.get(db, user_id)
    
    async def get_users(
        self, 
        skip: int = 0, 
        limit: int = 20,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """获取用户列表"""
        async with get_database() as db:
            filters = {}
            if is_active is not None:
                filters["is_active"] = is_active
                
            return await self.crud.get_multi(
                db, 
                skip=skip, 
                limit=limit,
                filters=filters,
                order_by="created_at",
                order_desc=True
            )
    
    async def update_user(self, user_id: str, update_data: dict) -> User:
        """更新用户"""
        async with get_database() as db:
            user = await self.crud.get(db, user_id)
            return await self.crud.update(db, user, update_data)
    
    async def deactivate_user(self, user_id: str) -> User:
        """停用用户"""
        return await self.update_user(user_id, {"is_active": False})
    
    async def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        async with get_database() as db:
            return await self.crud.delete(db, user_id)


class ProductService:
    """产品服务"""
    
    def __init__(self):
        self.crud = BaseCRUD(Product)
    
    async def create_product(self, product_data: dict) -> Product:
        """创建产品"""
        # 数据验证
        if not product_data.get("name"):
            raise ValidationError("产品名称不能为空", field="name")
        
        if not product_data.get("price") or product_data["price"] <= 0:
            raise ValidationError("产品价格必须大于0", field="price")
        
        async with get_database() as db:
            return await self.crud.create(db, product_data)
    
    async def get_product(self, product_id: str) -> Product:
        """获取产品"""
        async with get_database() as db:
            return await self.crud.get(db, product_id)
    
    async def get_products(
        self,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        include_deleted: bool = False
    ) -> List[Product]:
        """获取产品列表"""
        async with get_database() as db:
            filters = {}
            
            if category:
                filters["category"] = category
            
            if min_price is not None:
                filters["price"] = {"operator": "gte", "value": min_price}
            
            if max_price is not None:
                if "price" in filters:
                    # 如果已有价格过滤，需要处理范围查询
                    # 这里简化处理，实际应用中可能需要更复杂的查询构建
                    pass
                else:
                    filters["price"] = {"operator": "lte", "value": max_price}
            
            return await self.crud.get_multi(
                db,
                skip=skip,
                limit=limit,
                filters=filters,
                include_deleted=include_deleted,
                order_by="created_at",
                order_desc=True
            )
    
    async def update_product(self, product_id: str, update_data: dict) -> Product:
        """更新产品"""
        async with get_database() as db:
            product = await self.crud.get(db, product_id)
            return await self.crud.update(db, product, update_data)
    
    async def update_stock(self, product_id: str, quantity: int) -> Product:
        """更新库存"""
        async with get_database() as db:
            product = await self.crud.get(db, product_id)
            new_stock = product.stock + quantity
            
            if new_stock < 0:
                raise ValidationError(
                    f"库存不足，当前库存: {product.stock}",
                    field="stock"
                )
            
            return await self.crud.update(db, product, {"stock": new_stock})
    
    async def soft_delete_product(self, product_id: str) -> Product:
        """软删除产品"""
        async with get_database() as db:
            return await self.crud.soft_delete(db, product_id)
    
    async def restore_product(self, product_id: str) -> Product:
        """恢复产品"""
        async with get_database() as db:
            return await self.crud.restore(db, product_id)


# ================== 应用主逻辑 ==================

class ExampleApp:
    """示例应用"""
    
    def __init__(self):
        self.user_service = UserService()
        self.product_service = ProductService()
    
    async def initialize(self):
        """初始化应用"""
        print(f"🚀 正在启动 {app_settings.app_name}...")
        print(f"📊 环境: {app_settings.environment}")
        print(f"🗄️ 数据库: {app_settings.database.database_url}")
        
        # 初始化数据库
        await init_database()
        print("✅ 数据库初始化完成")
    
    async def demo_user_operations(self):
        """演示用户操作"""
        print("\n=== 用户管理演示 ===")
        
        try:
            # 创建用户
            print("1. 创建用户")
            users_data = [
                {
                    "username": "alice",
                    "email": "alice@example.com", 
                    "full_name": "Alice Johnson",
                    "age": 28
                },
                {
                    "username": "bob",
                    "email": "bob@example.com",
                    "full_name": "Bob Smith", 
                    "age": 32
                },
                {
                    "username": "charlie",
                    "email": "charlie@example.com",
                    "full_name": "Charlie Brown",
                    "age": 25
                }
            ]
            
            created_users = []
            for user_data in users_data:
                user = await self.user_service.create_user(user_data)
                created_users.append(user)
                print(f"   ✅ 创建用户: {user.username} ({user.full_name})")
            
            # 获取用户列表
            print("2. 获取用户列表")
            users = await self.user_service.get_users(limit=10)
            print(f"   📋 总用户数: {len(users)}")
            for user in users:
                status = "激活" if user.is_active else "停用"
                print(f"   - {user.username}: {user.full_name} ({status})")
            
            # 更新用户
            print("3. 更新用户")
            user = created_users[0]
            updated_user = await self.user_service.update_user(
                user.id, 
                {"age": 30, "full_name": "Alice Williams"}
            )
            print(f"   📝 更新用户: {updated_user.username} -> {updated_user.full_name}")
            
            # 停用用户
            print("4. 停用用户")
            deactivated_user = await self.user_service.deactivate_user(user.id)
            print(f"   ⏸️ 停用用户: {deactivated_user.username}")
            
            # 获取激活用户
            print("5. 获取激活用户")
            active_users = await self.user_service.get_users(is_active=True)
            print(f"   👥 激活用户数: {len(active_users)}")
            
        except Exception as e:
            print(f"   ❌ 用户操作错误: {e}")
    
    async def demo_product_operations(self):
        """演示产品操作"""
        print("\n=== 产品管理演示 ===")
        
        try:
            # 创建产品
            print("1. 创建产品")
            products_data = [
                {
                    "name": "iPhone 15 Pro",
                    "description": "苹果最新旗舰手机",
                    "price": 7999.0,
                    "stock": 50,
                    "category": "手机"
                },
                {
                    "name": "MacBook Pro M3",
                    "description": "专业笔记本电脑",
                    "price": 15999.0,
                    "stock": 30,
                    "category": "电脑"
                },
                {
                    "name": "AirPods Pro",
                    "description": "无线降噪耳机",
                    "price": 1999.0,
                    "stock": 100,
                    "category": "配件"
                }
            ]
            
            created_products = []
            for product_data in products_data:
                product = await self.product_service.create_product(product_data)
                created_products.append(product)
                print(f"   ✅ 创建产品: {product.name} (¥{product.price})")
            
            # 获取产品列表
            print("2. 获取产品列表")
            products = await self.product_service.get_products(limit=10)
            print(f"   📦 总产品数: {len(products)}")
            for product in products:
                print(f"   - {product.name}: ¥{product.price} (库存: {product.stock})")
            
            # 按分类查询
            print("3. 按分类查询")
            phone_products = await self.product_service.get_products(category="手机")
            print(f"   📱 手机产品: {[p.name for p in phone_products]}")
            
            # 更新库存
            print("4. 更新库存") 
            product = created_products[0]
            # 销售10个
            updated_product = await self.product_service.update_stock(product.id, -10)
            print(f"   📉 销售后库存: {product.name} -> {updated_product.stock}")
            
            # 补充库存
            restocked_product = await self.product_service.update_stock(product.id, 20)
            print(f"   📈 补充后库存: {product.name} -> {restocked_product.stock}")
            
            # 软删除产品
            print("5. 软删除产品")
            deleted_product = await self.product_service.soft_delete_product(product.id)
            print(f"   🗑️ 软删除产品: {deleted_product.name}")
            
            # 查看活跃产品
            active_products = await self.product_service.get_products()
            print(f"   📦 活跃产品数: {len(active_products)}")
            
            # 包含已删除的查询
            all_products = await self.product_service.get_products(include_deleted=True)
            print(f"   📦 总产品数（含已删除）: {len(all_products)}")
            
            # 恢复产品
            print("6. 恢复产品")
            restored_product = await self.product_service.restore_product(product.id)
            print(f"   ♻️ 恢复产品: {restored_product.name}")
            
        except Exception as e:
            print(f"   ❌ 产品操作错误: {e}")
    
    async def demo_error_handling(self):
        """演示错误处理"""
        print("\n=== 错误处理演示 ===")
        
        try:
            # 尝试创建重复用户名
            print("1. 尝试创建重复用户名")
            await self.user_service.create_user({
                "username": "alice",  # 已存在
                "email": "alice2@example.com",
                "full_name": "Alice Duplicate"
            })
        except ValidationError as e:
            print(f"   ✅ 捕获验证错误: {e.message}")
        
        try:
            # 尝试创建无效邮箱
            print("2. 尝试创建无效邮箱")
            await self.user_service.create_user({
                "username": "invalid",
                "email": "invalid-email",  # 无效格式
                "full_name": "Invalid User"
            })
        except ValidationError as e:
            print(f"   ✅ 捕获验证错误: {e.message}")
        
        try:
            # 尝试获取不存在的用户
            print("3. 尝试获取不存在的用户")
            await self.user_service.get_user("non-existent-id")
        except RecordNotFoundError as e:
            print(f"   ✅ 捕获记录不存在错误: {e.message}")
        
        try:
            # 尝试库存不足的操作
            print("4. 尝试库存不足的操作")
            products = await self.product_service.get_products(limit=1)
            if products:
                await self.product_service.update_stock(products[0].id, -1000)  # 超出库存
        except ValidationError as e:
            print(f"   ✅ 捕获库存不足错误: {e.message}")
    
    async def run(self):
        """运行应用"""
        await self.initialize()
        await self.demo_user_operations()
        await self.demo_product_operations()
        await self.demo_error_handling()
        
        print("\n🎉 示例应用运行完成！")
        print("\n💡 这个示例展示了:")
        print("  ✅ 完整的配置管理")
        print("  ✅ 数据库模型定义")
        print("  ✅ CRUD操作封装")
        print("  ✅ 业务逻辑分层")
        print("  ✅ 数据验证")
        print("  ✅ 错误处理")
        print("  ✅ 软删除功能")


# ================== 主入口 ==================

async def main():
    """主函数"""
    app = ExampleApp()
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
