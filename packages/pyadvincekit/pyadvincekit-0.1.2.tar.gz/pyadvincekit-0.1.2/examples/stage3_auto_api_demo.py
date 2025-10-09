"""
自动 API 生成功能演示

展示自动生成的 API 的具体功能和特性。
"""

import os
import sys
from pathlib import Path
from sqlalchemy.orm import Mapped, mapped_column

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pyadvincekit import (
    create_app, BaseModel, SoftDeleteModel, BaseCRUD, init_database
)
from pyadvincekit.models.base import create_required_string_column, create_text_column
from sqlalchemy import Integer, Boolean, Float
from typing import Optional


# 定义用户模型
class User(BaseModel):
    __tablename__ = "users"
    
    username: Mapped[str] = create_required_string_column(50, unique=True, comment="用户名")
    email: Mapped[str] = create_required_string_column(255, unique=True, comment="邮箱地址")
    full_name: Mapped[str] = create_required_string_column(100, comment="全名")
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="年龄")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")


# 定义产品模型（支持软删除）
class Product(SoftDeleteModel):
    __tablename__ = "products"
    
    name: Mapped[str] = create_required_string_column(200, comment="产品名称")
    description: Mapped[str] = create_text_column(comment="产品描述")
    price: Mapped[float] = mapped_column(Float, nullable=False, comment="价格")
    stock: Mapped[int] = mapped_column(Integer, default=0, comment="库存数量")
    category: Mapped[str] = create_required_string_column(50, comment="产品分类")


# 创建应用
app = create_app(
    title="自动 API 生成演示",
    description="演示 PyAdvanceKit 自动 API 生成功能",
    version="1.0.0"
)

# 自动生成用户管理 API
app.add_auto_api(
    model_class=User,
    router_prefix="/api/users",
    tags=["用户管理"]
)

# 自动生成产品管理 API（包含软删除功能）
app.add_auto_api(
    model_class=Product,
    router_prefix="/api/products",
    tags=["产品管理"],
    include_endpoints=["list", "create", "get", "update", "soft_delete", "restore"]
)

# 添加一些自定义路由来演示功能
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "PyAdvanceKit 自动 API 生成演示",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/api/demo")
async def demo():
    """演示页面"""
    return {
        "message": "自动生成的 API 功能演示",
        "features": [
            "自动生成 CRUD 操作",
            "统一响应格式",
            "自动分页支持",
            "搜索和过滤功能",
            "排序功能",
            "软删除支持",
            "自动数据验证",
            "OpenAPI 文档生成"
        ],
        "endpoints": {
            "users": {
                "list": "GET /api/users - 获取用户列表",
                "create": "POST /api/users - 创建用户",
                "get": "GET /api/users/{id} - 获取用户详情",
                "update": "PUT /api/users/{id} - 更新用户",
                "delete": "DELETE /api/users/{id} - 删除用户"
            },
            "products": {
                "list": "GET /api/products - 获取产品列表",
                "create": "POST /api/products - 创建产品",
                "get": "GET /api/products/{id} - 获取产品详情",
                "update": "PUT /api/products/{id} - 更新产品",
                "soft_delete": "DELETE /api/products/{id}/soft-delete - 软删除产品",
                "restore": "POST /api/products/{id}/restore - 恢复产品"
            }
        },
        "query_parameters": {
            "pagination": {
                "skip": "跳过的记录数（默认：0）",
                "limit": "每页记录数（默认：10，最大：100）"
            },
            "search": {
                "search": "搜索关键词（在所有字符串字段中搜索）"
            },
            "sorting": {
                "order_by": "排序字段",
                "order_desc": "是否降序（默认：false）"
            },
            "filtering": {
                "include_deleted": "是否包含已删除记录（仅软删除模型）"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    import asyncio
    # 导入配置相关模块
    from pyadvincekit.core.config import Settings
    from pyadvincekit.core.database import DatabaseManager
    from pyadvincekit.core import  set_database_manager
    
    async def startup():
        # settings = Settings(
        #     database={
        #         # "database_url": "sqlite:///./x_app1.db",
        #         "database_url": "mysql+aiomysql://root:123456@localhost/c_database",
        #         "echo_sql": True,
        #         "pool_size": 5
        #     },
        #     environment="development",
        #     debug=True
        # )
        #
        # # 使用自定义配置创建数据库管理器
        # db_manager = DatabaseManager(settings)
        # print("✅ 已创建自定义数据库管理器")
        # set_database_manager(db_manager)

        """启动时初始化数据库"""
        await init_database()
        print("✅ 数据库初始化完成")
        print("🚀 应用启动完成")
        print()
        print("📚 API 文档地址:")
        print("   - Swagger UI: http://localhost:8000/docs")
        print("   - ReDoc: http://localhost:8000/redoc")
        print("   - 演示页面: http://localhost:8000/api/demo")
        print()
        print("🔗 自动生成的 API 端点:")
        print()
        print("用户管理 API:")
        print("   GET    /api/users                    - 获取用户列表")
        print("   POST   /api/users                    - 创建用户")
        print("   GET    /api/users/{id}               - 获取用户详情")
        print("   PUT    /api/users/{id}               - 更新用户")
        print("   DELETE /api/users/{id}               - 删除用户")
        print()
        print("产品管理 API:")
        print("   GET    /api/products                 - 获取产品列表")
        print("   POST   /api/products                 - 创建产品")
        print("   GET    /api/products/{id}            - 获取产品详情")
        print("   PUT    /api/products/{id}            - 更新产品")
        print("   DELETE /api/products/{id}/soft-delete - 软删除产品")
        print("   POST   /api/products/{id}/restore    - 恢复产品")
        print()
        print("💡 使用示例:")
        print("   # 获取用户列表（分页）")
        print("   GET /api/users?skip=0&limit=10")
        print()
        print("   # 搜索用户")
        print("   GET /api/users?search=张三")
        print()
        print("   # 按年龄排序")
        print("   GET /api/users?order_by=age&order_desc=true")
        print()
        print("   # 创建用户")
        print("   POST /api/users")
        print("   {")
        print('     "username": "zhangsan",')
        print('     "email": "zhang@example.com",')
        print('     "full_name": "张三",')
        print('     "age": 25')
        print("   }")
    
    # 添加启动事件
    @app.on_event("startup")
    async def startup_event():
        await startup()
    
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=8000)
