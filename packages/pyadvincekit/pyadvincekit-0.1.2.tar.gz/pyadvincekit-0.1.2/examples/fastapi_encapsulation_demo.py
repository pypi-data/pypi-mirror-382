"""
PyAdvanceKit FastAPI 封装功能演示

展示 PyAdvanceKit 如何封装和增强 FastAPI 功能：
- 一行代码创建应用
- 自动API生成
- 统一响应格式
- 全局异常处理
- 中间件集成
- 配置管理
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import String, Integer, Boolean, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel as PydanticModel, Field

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pyadvincekit import (
    # 核心功能
    create_app, FastAPIAppFactory, FastAPIWithAutoAPI,
    # 数据库
    BaseModel, SoftDeleteModel, BaseCRUD, get_database, init_database,
    # 响应格式
    success_response, error_response, paginated_response,
    ResponseCode, ResponseMessage,
    # 中间件
    setup_all_middleware,
    # 配置
    Settings,
    # 自动API生成
    auto_generate_api, AutoAPIGenerator,
    # 工具函数
    get_logger, create_access_token, hash_password
)
from pyadvincekit.core.config import get_settings
from pyadvincekit.models.base import create_required_string_column, create_text_column
from pyadvincekit.core.exceptions import ValidationError as CustomValidationError, NotFoundError
from pyadvincekit.core.database import set_database_manager, DatabaseManager

# 配置日志
logger = get_logger(__name__)

# ================== 数据模型定义 ==================

class User(BaseModel):
    """用户模型"""
    __tablename__ = "demo_users"
    
    username: Mapped[str] = create_required_string_column(50, unique=True, comment="用户名")
    email: Mapped[str] = create_required_string_column(255, unique=True, comment="邮箱")
    full_name: Mapped[str] = create_required_string_column(100, comment="全名")
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="年龄")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="头像URL")


class Product(SoftDeleteModel):
    """产品模型（支持软删除）"""
    __tablename__ = "demo_products"
    
    name: Mapped[str] = create_required_string_column(200, comment="产品名称")
    description: Mapped[str] = create_text_column(comment="产品描述")
    price: Mapped[float] = mapped_column(Float, nullable=False, comment="价格")
    stock: Mapped[int] = mapped_column(Integer, default=0, comment="库存数量")
    category: Mapped[str] = create_required_string_column(50, comment="产品分类")
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否推荐")


class Order(BaseModel):
    """订单模型"""
    __tablename__ = "demo_orders"
    
    order_no: Mapped[str] = create_required_string_column(50, unique=True, comment="订单号")
    user_id: Mapped[str] = create_required_string_column(36, comment="用户ID")
    total_amount: Mapped[float] = mapped_column(Float, nullable=False, comment="总金额")
    status: Mapped[str] = mapped_column(String(20), default="pending", comment="订单状态")
    notes: Mapped[Optional[str]] = create_text_column(comment="备注")


# ================== Pydantic 模型 ==================

class UserCreate(PydanticModel):
    """用户创建模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., description="邮箱地址")
    full_name: str = Field(..., min_length=2, max_length=100, description="全名")
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄")
    avatar_url: Optional[str] = Field(None, description="头像URL")


class UserUpdate(PydanticModel):
    """用户更新模型"""
    email: Optional[str] = Field(None, description="邮箱地址")
    full_name: Optional[str] = Field(None, min_length=2, max_length=100, description="全名")
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄")
    is_active: Optional[bool] = Field(None, description="是否激活")
    avatar_url: Optional[str] = Field(None, description="头像URL")


class ProductCreate(PydanticModel):
    """产品创建模型"""
    name: str = Field(..., min_length=2, max_length=200, description="产品名称")
    description: str = Field(..., description="产品描述")
    price: float = Field(..., gt=0, description="价格")
    stock: int = Field(0, ge=0, description="库存数量")
    category: str = Field(..., min_length=2, max_length=50, description="产品分类")
    is_featured: bool = Field(False, description="是否推荐")


class ProductUpdate(PydanticModel):
    """产品更新模型"""
    name: Optional[str] = Field(None, min_length=2, max_length=200, description="产品名称")
    description: Optional[str] = Field(None, description="产品描述")
    price: Optional[float] = Field(None, gt=0, description="价格")
    stock: Optional[int] = Field(None, ge=0, description="库存数量")
    category: Optional[str] = Field(None, min_length=2, max_length=50, description="产品分类")
    is_featured: Optional[bool] = Field(None, description="是否推荐")


# ================== 演示1：一行代码创建应用 ==================

def demo_simple_app():
    """演示：一行代码创建FastAPI应用"""
    print("🚀 演示1：一行代码创建FastAPI应用")
    print("=" * 50)
    
    # 一行代码创建应用
    app = create_app(
        title="PyAdvanceKit 演示应用",
        description="展示PyAdvanceKit的强大功能",
        version="1.0.0"
    )
    
    print("✅ 应用创建成功！")
    print(f"📝 应用标题: {app.title}")
    print(f"📝 应用版本: {app.version}")
    print(f"📝 路由数量: {len(app.routes)}")
    print()
    
    return app


# ================== 演示2：自动API生成 ==================

def demo_auto_api_generation():
    """演示：自动API生成功能"""
    print("🤖 演示2：自动API生成功能")
    print("=" * 50)
    
    # 创建支持自动API的应用
    app = create_app(
        title="自动API生成演示",
        description="展示自动API生成功能",
        version="1.0.0"
    )
    
    # 自动生成用户管理API
    app.add_auto_api(
        model_class=User,
        router_prefix="/api/users",
        tags=["用户管理"],
        include_endpoints=["list", "create", "get", "update", "delete"]
    )
    
    # 自动生成产品管理API（包含软删除）
    app.add_auto_api(
        model_class=Product,
        router_prefix="/api/products",
        tags=["产品管理"],
        include_endpoints=["list", "create", "get", "update", "soft_delete", "restore"]
    )
    
    print("✅ 自动API生成完成！")
    print("📋 生成的API端点:")
    
    # 统计路由
    user_routes = [route for route in app.routes if hasattr(route, 'path') and '/api/users' in route.path]
    product_routes = [route for route in app.routes if hasattr(route, 'path') and '/api/products' in route.path]
    
    print(f"   👥 用户管理: {len(user_routes)} 个端点")
    print(f"   📦 产品管理: {len(product_routes)} 个端点")
    print()
    
    return app


# ================== 演示3：统一响应格式 ==================

def demo_unified_response():
    """演示：统一响应格式"""
    print("📋 演示3：统一响应格式")
    print("=" * 50)
    
    app = create_app(title="统一响应格式演示")
    
    # 创建测试路由
    test_router = APIRouter(prefix="/api/test", tags=["测试"])
    
    @test_router.get("/success")
    async def test_success():
        """测试成功响应"""
        return success_response(
            data={"message": "操作成功", "timestamp": "2024-01-01T00:00:00Z"},
            message="请求处理成功"
        )
    
    @test_router.get("/error")
    async def test_error():
        """测试错误响应"""
        return error_response(
            message="这是一个测试错误",
            code=ResponseCode.BAD_REQUEST,
            details={"field": "test_field", "reason": "validation_failed"}
        )
    
    @test_router.get("/paginated")
    async def test_paginated():
        """测试分页响应"""
        # 模拟分页数据
        items = [
            {"id": i, "name": f"项目 {i}", "value": i * 10}
            for i in range(1, 6)
        ]
        
        return paginated_response(
            items=items,
            page=1,
            page_size=5,
            total=25,
            message="分页数据获取成功"
        )
    
    app.include_router(test_router)
    
    print("✅ 统一响应格式演示完成！")
    print("📋 响应格式特点:")
    print("   ✅ 成功响应: {code: 0, message: 'success', data: {...}}")
    print("   ❌ 错误响应: {code: 400, message: 'error', data: null, details: {...}}")
    print("   📄 分页响应: {code: 0, message: 'success', data: {items: [...], meta: {...}}}")
    print()
    
    return app


# ================== 演示4：全局异常处理 ==================

def demo_global_exception_handling():
    """演示：全局异常处理"""
    print("🛡️ 演示4：全局异常处理")
    print("=" * 50)
    
    app = create_app(title="全局异常处理演示")
    
    # 创建测试路由
    exception_router = APIRouter(prefix="/api/exception", tags=["异常处理"])
    
    @exception_router.get("/validation-error")
    async def test_validation_error():
        """测试验证错误"""
        raise CustomValidationError("数据验证失败", field="username")
    
    @exception_router.get("/not-found-error")
    async def test_not_found_error():
        """测试资源不存在错误"""
        raise NotFoundError("用户不存在", resource="User", resource_id="123")
    
    @exception_router.get("/http-error")
    async def test_http_error():
        """测试HTTP错误"""
        raise HTTPException(status_code=403, detail="权限不足")
    
    @exception_router.get("/server-error")
    async def test_server_error():
        """测试服务器错误"""
        raise Exception("这是一个未处理的异常")
    
    app.include_router(exception_router)
    
    print("✅ 全局异常处理演示完成！")
    print("🛡️ 异常处理特点:")
    print("   ✅ 自动捕获所有异常")
    print("   ✅ 统一错误响应格式")
    print("   ✅ 开发/生产环境差异化")
    print("   ✅ 自动记录异常日志")
    print()
    
    return app


# ================== 演示5：中间件集成 ==================

def demo_middleware_integration():
    """演示：中间件集成"""
    print("🔧 演示5：中间件集成")
    print("=" * 50)
    
    # 使用应用工厂进行高级配置
    factory = FastAPIAppFactory()
    
    app = factory.create_app(
        title="中间件集成演示",
        description="展示各种中间件功能",
        version="1.0.0",
        include_health_check=True,
        include_database_init=False
    )
    
    # 添加测试路由
    middleware_router = APIRouter(prefix="/api/middleware", tags=["中间件"])
    
    @middleware_router.get("/request-info")
    async def get_request_info(request):
        """获取请求信息（展示请求ID中间件）"""
        return success_response({
            "request_id": getattr(request.state, "request_id", None),
            "user_agent": request.headers.get("user-agent"),
            "client_ip": request.client.host if request.client else None,
            "method": request.method,
            "path": request.url.path
        })
    
    @middleware_router.get("/performance-test")
    async def performance_test():
        """性能测试端点（展示性能监控中间件）"""
        import time
        time.sleep(0.1)  # 模拟处理时间
        return success_response({"message": "性能测试完成"})
    
    app.include_router(middleware_router)
    
    print("✅ 中间件集成演示完成！")
    print("🔧 集成的中间件:")
    print("   📝 请求日志中间件: 记录所有请求和响应")
    print("   ⚡ 性能监控中间件: 监控响应时间和资源使用")
    print("   🆔 请求ID中间件: 为每个请求生成唯一ID")
    print("   🔒 安全头中间件: 添加安全相关的HTTP头")
    print("   🌐 CORS中间件: 处理跨域请求")
    print()
    
    return app


# ================== 演示6：配置管理 ==================

def demo_configuration_management():
    """演示：配置管理"""
    print("⚙️ 演示6：配置管理")
    print("=" * 50)
    
    # 获取当前配置
    settings = get_settings()
    
    print("📋 当前配置信息:")
    print(f"   🌍 环境: {settings.environment}")
    print(f"   🐛 调试模式: {settings.debug}")
    print(f"   📊 日志级别: {settings.logging.log_level}")
    print(f"   🗄️ 数据库URL: {settings.database.database_url}")
    print(f"   🔗 连接池大小: {settings.database.pool_size}")
    print()
    
    # 演示自定义配置
    custom_settings = Settings(
        environment="development",
        debug=True,
        logging={
            "log_level": "DEBUG",
            "log_format": "json"
        },
        database={
            "database_url": "sqlite+aiosqlite:///./demo.db",
            "echo_sql": True,
            "pool_size": 5
        }
    )
    
    print("🔧 自定义配置演示:")
    print(f"   🌍 环境: {custom_settings.environment}")
    print(f"   🐛 调试模式: {custom_settings.debug}")
    print(f"   📊 日志级别: {custom_settings.logging.log_level}")
    print(f"   🗄️ 数据库URL: {custom_settings.database.database_url}")
    print()
    
    return custom_settings


# ================== 演示7：完整业务应用 ==================

def demo_complete_business_app():
    """演示：完整业务应用"""
    print("🏢 演示7：完整业务应用")
    print("=" * 50)
    
    # 创建完整的业务应用
    app = create_app(
        title="电商系统演示",
        description="展示完整的业务应用功能",
        version="1.0.0"
    )
    
    # 自动生成所有API
    app.add_auto_api(User, router_prefix="/api/users", tags=["用户管理"])
    app.add_auto_api(Product, router_prefix="/api/products", tags=["产品管理"])
    app.add_auto_api(Order, router_prefix="/api/orders", tags=["订单管理"])
    
    # 添加业务逻辑路由
    business_router = APIRouter(prefix="/api/business", tags=["业务逻辑"])
    
    @business_router.get("/stats")
    async def get_business_stats():
        """获取业务统计信息"""
        return success_response({
            "total_users": 1000,
            "total_products": 500,
            "total_orders": 2500,
            "revenue": 125000.50,
            "active_users": 750
        })
    
    @business_router.post("/users/{user_id}/orders")
    async def create_user_order(user_id: str, order_data: dict):
        """为用户创建订单"""
        # 这里可以添加业务逻辑
        return success_response({
            "order_id": "ORD-2024-001",
            "user_id": user_id,
            "status": "created",
            "total_amount": order_data.get("total_amount", 0)
        })
    
    app.include_router(business_router)
    
    print("✅ 完整业务应用创建成功！")
    print("🏢 应用功能:")
    print("   👥 用户管理: 完整的CRUD操作")
    print("   📦 产品管理: 支持软删除的产品管理")
    print("   📋 订单管理: 订单创建和状态管理")
    print("   📊 业务统计: 实时业务数据统计")
    print("   🔄 自动API: 所有模型自动生成API端点")
    print()
    
    return app


# ================== PyAdvanceKit 封装功能演示应用 ==================

def create_encapsulation_demo_app():
    """创建 PyAdvanceKit 封装功能演示应用"""
    print("🚀 创建 PyAdvanceKit 封装功能演示应用...")
    
    # ================== 演示1：一行代码创建应用 ==================
    print("📝 演示1：一行代码创建应用")
    print("   原生FastAPI需要：")
    print("   - 手动创建FastAPI实例")
    print("   - 手动配置中间件")
    print("   - 手动设置异常处理器")
    print("   - 手动配置CORS等")
    print()
    print("   PyAdvanceKit封装后：")
    print("   app = create_app()  # 一行代码搞定所有配置")
    print()
    
    # 一行代码创建完整的应用
    app = create_app(
        title="PyAdvanceKit 封装功能演示",
        description="展示 PyAdvanceKit 如何封装和增强 FastAPI 功能",
        version="1.0.0"
    )
    
    # ================== 演示2：自动API生成 ==================
    print("📝 演示2：自动API生成")
    print("   原生FastAPI需要：")
    print("   - 手动编写每个CRUD端点")
    print("   - 手动处理分页、搜索、排序")
    print("   - 手动编写Pydantic模型")
    print("   - 手动处理异常")
    print()
    print("   PyAdvanceKit封装后：")
    print("   app.add_auto_api(User)  # 自动生成完整CRUD API")
    print()
    
    # 自动生成所有业务API
    app.add_auto_api(User, router_prefix="/api/users", tags=["用户管理"])
    app.add_auto_api(Product, router_prefix="/api/products", tags=["产品管理"])
    app.add_auto_api(Order, router_prefix="/api/orders", tags=["订单管理"])
    
    # ================== 演示3：统一响应格式 ==================
    print("📝 演示3：统一响应格式")
    print("   原生FastAPI：")
    print("   - 每个端点返回格式不统一")
    print("   - 需要手动处理错误响应")
    print("   - 分页响应格式不一致")
    print()
    print("   PyAdvanceKit封装后：")
    print("   - 自动统一响应格式")
    print("   - 自动错误处理")
    print("   - 标准分页响应")
    print()
    
    # 添加封装功能演示路由
    demo_router = APIRouter(prefix="/api/encapsulation-demo", tags=["封装功能演示"])
    
    @demo_router.get("/")
    async def encapsulation_overview():
        """PyAdvanceKit 封装功能概览"""
        return success_response({
            "message": "PyAdvanceKit FastAPI 封装功能演示",
            "encapsulation_features": {
                "一行代码创建应用": {
                    "原生FastAPI": "需要手动配置中间件、异常处理、CORS等",
                    "PyAdvanceKit": "create_app() 一行代码完成所有配置",
                    "优势": "减少90%的初始化代码"
                },
                "自动API生成": {
                    "原生FastAPI": "需要手动编写每个CRUD端点",
                    "PyAdvanceKit": "app.add_auto_api(Model) 自动生成完整API",
                    "优势": "减少80%的重复代码"
                },
                "统一响应格式": {
                    "原生FastAPI": "每个端点返回格式不统一",
                    "PyAdvanceKit": "自动统一响应格式，标准错误处理",
                    "优势": "API响应格式完全一致"
                },
                "全局异常处理": {
                    "原生FastAPI": "需要手动编写异常处理器",
                    "PyAdvanceKit": "自动捕获和处理所有异常",
                    "优势": "无需关心异常处理细节"
                },
                "中间件集成": {
                    "原生FastAPI": "需要手动配置各种中间件",
                    "PyAdvanceKit": "自动集成日志、性能监控、安全等中间件",
                    "优势": "开箱即用的生产级中间件"
                }
            }
        })
    
    @demo_router.get("/response-comparison")
    async def response_comparison():
        """响应格式对比演示"""
        return success_response({
            "原生FastAPI响应": {
                "成功": {"data": "some data"},
                "错误": {"detail": "error message"},
                "分页": {"items": [], "total": 100}
            },
            "PyAdvanceKit统一响应": {
                "成功": {"code": 0, "message": "success", "data": "some data"},
                "错误": {"code": 400, "message": "error", "data": null, "details": {}},
                "分页": {"code": 0, "message": "success", "data": {"items": [], "meta": {}}}
            },
            "优势": "完全统一的响应格式，便于前端处理"
        })
    
    @demo_router.get("/api-generation-demo")
    async def api_generation_demo():
        """自动API生成演示"""
        return success_response({
            "自动生成的API端点": {
                "用户管理": [
                    "GET /api/users - 获取用户列表（支持分页、搜索、排序）",
                    "POST /api/users - 创建用户",
                    "GET /api/users/{id} - 获取用户详情",
                    "PUT /api/users/{id} - 更新用户",
                    "DELETE /api/users/{id} - 删除用户"
                ],
                "产品管理": [
                    "GET /api/products - 获取产品列表",
                    "POST /api/products - 创建产品",
                    "GET /api/products/{id} - 获取产品详情",
                    "PUT /api/products/{id} - 更新产品",
                    "DELETE /api/products/{id}/soft-delete - 软删除产品",
                    "POST /api/products/{id}/restore - 恢复产品"
                ],
                "订单管理": [
                    "GET /api/orders - 获取订单列表",
                    "POST /api/orders - 创建订单",
                    "GET /api/orders/{id} - 获取订单详情",
                    "PUT /api/orders/{id} - 更新订单",
                    "DELETE /api/orders/{id} - 删除订单"
                ]
            },
            "自动功能": [
                "分页支持（skip, limit参数）",
                "搜索功能（search参数）",
                "排序功能（order_by, order_desc参数）",
                "过滤功能（include_deleted参数）",
                "数据验证（自动Pydantic模型）",
                "错误处理（统一异常处理）"
            ]
        })
    
    @demo_router.get("/middleware-demo")
    async def middleware_demo(request):
        """中间件功能演示"""
        return success_response({
            "自动集成的中间件": {
                "请求日志中间件": "自动记录所有请求和响应",
                "性能监控中间件": "自动监控响应时间和资源使用",
                "请求ID中间件": "为每个请求生成唯一ID",
                "安全头中间件": "自动添加安全相关的HTTP头",
                "CORS中间件": "自动处理跨域请求"
            },
            "当前请求信息": {
                "request_id": getattr(request.state, "request_id", None),
                "user_agent": request.headers.get("user-agent"),
                "client_ip": request.client.host if request.client else None,
                "method": request.method,
                "path": request.url.path
            },
            "优势": "无需手动配置，开箱即用"
        })
    
    @demo_router.get("/exception-handling-demo")
    async def exception_handling_demo():
        """异常处理演示"""
        return success_response({
            "自动异常处理": {
                "验证错误": "自动捕获ValidationError并返回统一格式",
                "资源不存在": "自动捕获NotFoundError并返回404",
                "HTTP错误": "自动捕获HTTPException并返回对应状态码",
                "服务器错误": "自动捕获所有未处理异常并返回500",
                "数据库错误": "自动捕获数据库异常并返回友好错误信息"
            },
            "异常处理优势": [
                "无需在每个端点手动处理异常",
                "统一的错误响应格式",
                "自动记录异常日志",
                "开发/生产环境差异化处理"
            ]
        })
    
    # ================== 演示4：异常处理对比 ==================
    print("📝 演示4：异常处理对比")
    print("   原生FastAPI：")
    print("   - 需要手动编写异常处理器")
    print("   - 每个端点需要try-catch")
    print("   - 错误响应格式不统一")
    print()
    print("   PyAdvanceKit封装后：")
    print("   - 自动捕获所有异常")
    print("   - 统一错误响应格式")
    print("   - 自动记录异常日志")
    print()
    
    # 添加异常处理演示路由
    exception_router = APIRouter(prefix="/api/exception-demo", tags=["异常处理演示"])
    
    @exception_router.get("/validation-error")
    async def demo_validation_error():
        """演示验证错误处理（PyAdvanceKit自动处理）"""
        raise CustomValidationError("PyAdvanceKit自动捕获并处理验证错误", field="demo_field")
    
    @exception_router.get("/not-found-error")
    async def demo_not_found_error():
        """演示资源不存在错误处理（PyAdvanceKit自动处理）"""
        raise NotFoundError("PyAdvanceKit自动捕获并处理资源不存在错误", resource="DemoResource", resource_id="demo-123")
    
    @exception_router.get("/http-error")
    async def demo_http_error():
        """演示HTTP错误处理（PyAdvanceKit自动处理）"""
        raise HTTPException(status_code=403, detail="PyAdvanceKit自动捕获并处理HTTP错误")
    
    @exception_router.get("/server-error")
    async def demo_server_error():
        """演示服务器错误处理（PyAdvanceKit自动处理）"""
        raise Exception("PyAdvanceKit自动捕获并处理服务器错误")
    
    # 注册所有路由
    app.include_router(demo_router)
    app.include_router(exception_router)
    
    # ================== 演示5：配置管理对比 ==================
    print("📝 演示5：配置管理对比")
    print("   原生FastAPI：")
    print("   - 需要手动管理配置")
    print("   - 环境变量处理复杂")
    print("   - 配置验证需要额外代码")
    print()
    print("   PyAdvanceKit封装后：")
    print("   - 自动配置管理")
    print("   - 类型安全的配置验证")
    print("   - 多环境配置支持")
    print()
    
    # 添加根路径
    @app.get("/")
    async def root():
        """根路径 - PyAdvanceKit 封装功能演示"""
        settings = get_settings()
        return success_response({
            "message": "PyAdvanceKit FastAPI 封装功能演示",
            "description": "展示 PyAdvanceKit 如何封装和增强 FastAPI 功能",
            "version": "1.0.0",
            "encapsulation_benefits": {
                "开发效率": "减少80%的重复代码",
                "代码质量": "统一的架构和最佳实践",
                "维护成本": "标准化的错误处理和日志记录",
                "学习成本": "开箱即用，无需学习复杂配置"
            },
            "quick_start": {
                "docs": "/docs - 查看完整的API文档",
                "redoc": "/redoc - 查看ReDoc格式的API文档",
                "encapsulation_demo": "/api/encapsulation-demo - 查看封装功能演示",
                "auto_generated_apis": {
                    "users": "/api/users - 自动生成的用户管理API",
                    "products": "/api/products - 自动生成的产品管理API（支持软删除）",
                    "orders": "/api/orders - 自动生成的订单管理API"
                },
                "exception_demo": "/api/exception-demo - 查看异常处理演示"
            },
            "current_config": {
                "environment": settings.environment,
                "debug": settings.debug,
                "database_url": settings.database.database_url,
                "log_level": settings.logging.log_level
            }
        })
    
    print("✅ PyAdvanceKit 封装功能演示应用创建完成！")
    return app


# ================== 创建应用实例 ==================

# 创建PyAdvanceKit封装功能演示应用
app = create_encapsulation_demo_app()


# ================== 启动函数 ==================

async def startup():
    """应用启动时的初始化"""
    print("🗄️ 初始化数据库...")
    await init_database()
    print("✅ 数据库初始化完成")
    print()
    print("🎉 PyAdvanceKit 封装功能演示应用启动成功！")
    print("=" * 60)
    print("🌐 访问地址:")
    print("   📚 API文档: http://localhost:8000/docs")
    print("   📖 ReDoc文档: http://localhost:8000/redoc")
    print("   🏠 首页: http://localhost:8000/")
    print("   🎯 封装功能演示: http://localhost:8000/api/encapsulation-demo/")
    print()
    print("🔗 PyAdvanceKit 自动生成的API端点:")
    print("   👥 用户管理: http://localhost:8000/api/users")
    print("   📦 产品管理: http://localhost:8000/api/products")
    print("   📋 订单管理: http://localhost:8000/api/orders")
    print()
    print("💡 PyAdvanceKit 封装功能演示:")
    print("   • 一行代码创建应用 - create_app() 完成所有配置")
    print("   • 自动API生成 - app.add_auto_api() 自动生成完整CRUD API")
    print("   • 统一响应格式 - 标准化的API响应结构")
    print("   • 全局异常处理 - 自动捕获和处理所有异常")
    print("   • 中间件集成 - 请求日志、性能监控、安全头等")
    print("   • 配置管理 - 多环境配置支持")
    print("   • 软删除支持 - 产品模型支持软删除和恢复")
    print()
    print("📊 对比原生FastAPI的优势:")
    print("   • 减少80%的重复代码")
    print("   • 减少90%的初始化代码")
    print("   • 统一的架构和最佳实践")
    print("   • 开箱即用的生产级功能")
    print()


# 添加启动事件
@app.on_event("startup")
async def startup_event():
    await startup()


# ================== 主函数 ==================

def main():
    """主函数 - 启动 PyAdvanceKit 封装功能演示应用"""
    import uvicorn
    
    print("🚀 启动 PyAdvanceKit 封装功能演示应用...")
    print("=" * 60)
    print("📝 这个应用专门演示 PyAdvanceKit 如何封装和增强 FastAPI 功能")
    print("📝 对比原生 FastAPI 和 PyAdvanceKit 的差异")
    print("📝 展示 PyAdvanceKit 的封装优势")
    print("=" * 60)
    
    # 启动服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
