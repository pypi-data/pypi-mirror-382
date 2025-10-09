"""
PyAdvanceKit FastAPI 封装功能测试

参考 stage3_fastapi_integration.py 的功能，专门测试 PyAdvanceKit 如何封装和增强 FastAPI：
- 对比原生 FastAPI 和 PyAdvanceKit 的差异
- 测试 PyAdvanceKit 的封装功能
- 展示 PyAdvanceKit 的优势
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import String, Integer, Boolean, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel as PydanticModel, Field

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pyadvincekit import (
    # 应用工厂
    create_app, FastAPIAppFactory,
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
    __tablename__ = "test_users"
    
    username: Mapped[str] = create_required_string_column(50, unique=True, comment="用户名")
    email: Mapped[str] = create_required_string_column(255, unique=True, comment="邮箱")
    full_name: Mapped[str] = create_required_string_column(100, comment="全名")
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="年龄")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")


class Product(SoftDeleteModel):
    """产品模型（支持软删除）"""
    __tablename__ = "test_products"
    
    name: Mapped[str] = create_required_string_column(200, comment="产品名称")
    description: Mapped[str] = create_text_column(comment="产品描述")
    price: Mapped[float] = mapped_column(Float, nullable=False, comment="价格")
    stock: Mapped[int] = mapped_column(Integer, default=0, comment="库存数量")
    category: Mapped[str] = create_required_string_column(50, comment="产品分类")


# ================== Pydantic 模型 ==================

class UserCreate(PydanticModel):
    """用户创建模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., description="邮箱地址")
    full_name: str = Field(..., min_length=2, max_length=100, description="全名")
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄")


class UserUpdate(PydanticModel):
    """用户更新模型"""
    email: Optional[str] = Field(None, description="邮箱地址")
    full_name: Optional[str] = Field(None, min_length=2, max_length=100, description="全名")
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄")
    is_active: Optional[bool] = Field(None, description="是否激活")


class ProductCreate(PydanticModel):
    """产品创建模型"""
    name: str = Field(..., min_length=2, max_length=200, description="产品名称")
    description: str = Field(..., description="产品描述")
    price: float = Field(..., gt=0, description="价格")
    stock: int = Field(0, ge=0, description="库存数量")
    category: str = Field(..., min_length=2, max_length=50, description="产品分类")


# ================== 生命周期事件处理器 ==================

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    """应用生命周期管理"""
    # 启动时执行
    print("🗄️ 初始化数据库...")
    await init_database()
    print("✅ 数据库初始化完成")
    print()
    print("🎉 PyAdvanceKit 封装功能测试应用启动成功！")
    print("=" * 60)
    print("🌐 访问地址:")
    print("   📚 API文档: http://localhost:8000/docs")
    print("   📖 ReDoc文档: http://localhost:8000/redoc")
    print("   🏠 首页: http://localhost:8000/")
    print("   🧪 功能测试: http://localhost:8000/api/test/")
    print()
    print("🔗 PyAdvanceKit 自动生成的API端点:")
    print("   👥 用户管理: http://localhost:8000/api/users")
    print("   📦 产品管理: http://localhost:8000/api/products")
    print()
    print("🧪 测试端点:")
    print("   📋 测试概览: http://localhost:8000/api/test/")
    print("   📄 响应格式: http://localhost:8000/api/test/response-format")
    print("   🔧 中间件: http://localhost:8000/api/test/middleware-test")
    print("   ⚡ 性能: http://localhost:8000/api/test/performance-test")
    print("   ⚙️ 配置: http://localhost:8000/api/test/config-test")
    print("   🔄 CRUD对比: http://localhost:8000/api/crud-test/")
    print("   ❌ 异常处理: http://localhost:8000/api/exception-test/")
    print()
    print("💡 PyAdvanceKit 封装功能测试:")
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
    
    yield
    
    # 关闭时执行（如果需要的话）
    print("🔄 应用正在关闭...")


# ================== 创建 PyAdvanceKit 封装功能测试应用 ==================

def create_pyadvincekit_test_app():
    """创建 PyAdvanceKit 封装功能测试应用"""
    print("🚀 创建 PyAdvanceKit 封装功能测试应用...")
    print("=" * 60)
    
    # ================== 测试1：一行代码创建应用 ==================
    print("📝 测试1：一行代码创建应用")
    print("   原生FastAPI需要手动配置：")
    print("   - 创建FastAPI实例")
    print("   - 配置中间件（CORS、日志、性能监控等）")
    print("   - 设置异常处理器")
    print("   - 配置路由")
    print()
    print("   PyAdvanceKit封装后：")
    print("   app = create_app()  # 一行代码完成所有配置")
    print()
    
    # 使用 PyAdvanceKit 一行代码创建应用
    app = create_app(
        title="PyAdvanceKit 封装功能测试",
        description="测试 PyAdvanceKit 如何封装和增强 FastAPI 功能",
        version="1.0.0"
    )
    
    # 添加生命周期事件处理器
    app.router.lifespan_context = lifespan
    
    # ================== 测试2：自动API生成 ==================
    print("📝 测试2：自动API生成")
    print("   原生FastAPI需要手动编写：")
    print("   - 每个CRUD端点")
    print("   - 分页、搜索、排序逻辑")
    print("   - 数据验证")
    print("   - 异常处理")
    print()
    print("   PyAdvanceKit封装后：")
    print("   app.add_auto_api(User)  # 自动生成完整CRUD API")
    print()
    
    # 自动生成API
    app.add_auto_api(User, router_prefix="/api/users", tags=["用户管理"])
    app.add_auto_api(Product, router_prefix="/api/products", tags=["产品管理"])
    
    # ================== 测试3：统一响应格式 ==================
    print("📝 测试3：统一响应格式")
    print("   原生FastAPI响应格式不统一")
    print("   PyAdvanceKit自动统一响应格式")
    print()
    
    # 添加测试路由
    test_router = APIRouter(prefix="/api/test", tags=["PyAdvanceKit 封装测试"])
    
    @test_router.get("/")
    async def test_overview():
        """PyAdvanceKit 封装功能测试概览"""
        return success_response({
            "message": "PyAdvanceKit FastAPI 封装功能测试",
            "test_categories": {
                "应用创建": "一行代码创建完整的FastAPI应用",
                "自动API生成": "从模型自动生成完整的CRUD API",
                "统一响应格式": "标准化的API响应结构",
                "全局异常处理": "自动捕获和处理所有异常",
                "中间件集成": "自动集成生产级中间件",
                "配置管理": "类型安全的配置管理"
            },
            "comparison": {
                "原生FastAPI": "需要大量手动配置和重复代码",
                "PyAdvanceKit": "开箱即用，减少80%的重复代码"
            }
        })
    
    @test_router.get("/response-format")
    async def test_response_format():
        """测试统一响应格式"""
        return success_response({
            "message": "这是PyAdvanceKit的统一响应格式",
            "format": {
                "code": 0,
                "message": "success",
                "data": "实际数据"
            },
            "advantages": [
                "完全统一的响应格式",
                "便于前端处理",
                "自动错误处理",
                "标准分页响应"
            ]
        })
    
    @test_router.get("/middleware-test")
    async def test_middleware(request: Request):
        """测试中间件功能"""
        return success_response({
            "message": "PyAdvanceKit 中间件功能测试",
            "request_info": {
                "request_id": getattr(request.state, "request_id", None),
                "user_agent": request.headers.get("user-agent"),
                "client_ip": request.client.host if request.client else None,
                "method": request.method,
                "path": request.url.path
            },
            "middleware_features": [
                "请求日志记录",
                "性能监控",
                "请求ID生成",
                "安全头设置",
                "CORS处理"
            ],
            "note": "这些中间件都是PyAdvanceKit自动集成的"
        })
    
    @test_router.get("/performance-test")
    async def test_performance():
        """测试性能监控"""
        start_time = time.time()
        time.sleep(0.1)  # 模拟处理时间
        end_time = time.time()
        
        return success_response({
            "message": "性能监控测试",
            "processing_time": f"{end_time - start_time:.3f}秒",
            "note": "PyAdvanceKit自动监控性能，查看日志获取详细信息"
        })
    
    @test_router.get("/config-test")
    async def test_config():
        """测试配置管理"""
        settings = get_settings()
        return success_response({
            "message": "配置管理测试",
            "current_config": {
                "environment": settings.environment,
                "debug": settings.debug,
                "database_url": settings.database.database_url,
                "log_level": settings.logging.log_level
            },
            "advantages": [
                "类型安全的配置验证",
                "多环境配置支持",
                "环境变量自动覆盖",
                "配置热重载"
            ]
        })
    
    # ================== 测试4：异常处理 ==================
    print("📝 测试4：异常处理")
    print("   原生FastAPI需要手动处理异常")
    print("   PyAdvanceKit自动捕获和处理所有异常")
    print()
    
    # 添加异常处理测试路由
    exception_router = APIRouter(prefix="/api/exception-test", tags=["异常处理测试"])
    
    @exception_router.get("/validation-error")
    async def test_validation_error():
        """测试验证错误处理"""
        raise CustomValidationError("PyAdvanceKit自动处理验证错误", field="test_field")
    
    @exception_router.get("/not-found-error")
    async def test_not_found_error():
        """测试资源不存在错误处理"""
        raise NotFoundError("PyAdvanceKit自动处理资源不存在错误", resource_type="TestResource", resource_id="test-123")
    
    @exception_router.get("/http-error")
    async def test_http_error():
        """测试HTTP错误处理"""
        raise HTTPException(status_code=403, detail="PyAdvanceKit自动处理HTTP错误")
    
    @exception_router.get("/server-error")
    async def test_server_error():
        """测试服务器错误处理"""
        raise Exception("PyAdvanceKit自动处理服务器错误")
    
    # ================== 测试5：CRUD操作对比 ==================
    print("📝 测试5：CRUD操作对比")
    print("   原生FastAPI需要手动编写CRUD端点")
    print("   PyAdvanceKit自动生成完整的CRUD API")
    print()
    
    # 添加CRUD对比测试路由
    crud_router = APIRouter(prefix="/api/crud-test", tags=["CRUD操作测试"])
    
    @crud_router.get("/manual-crud-demo")
    async def manual_crud_demo():
        """演示原生FastAPI需要手动编写的CRUD操作"""
        return success_response({
            "message": "原生FastAPI需要手动编写的CRUD操作",
            "manual_work": [
                "手动编写GET /users端点",
                "手动编写POST /users端点",
                "手动编写GET /users/{id}端点",
                "手动编写PUT /users/{id}端点",
                "手动编写DELETE /users/{id}端点",
                "手动处理分页逻辑",
                "手动处理搜索逻辑",
                "手动处理排序逻辑",
                "手动处理数据验证",
                "手动处理异常"
            ],
            "code_lines": "每个模型需要约200-300行代码"
        })
    
    @crud_router.get("/auto-crud-demo")
    async def auto_crud_demo():
        """演示PyAdvanceKit自动生成的CRUD操作"""
        return success_response({
            "message": "PyAdvanceKit自动生成的CRUD操作",
            "auto_generated": [
                "自动生成GET /api/users端点（支持分页、搜索、排序）",
                "自动生成POST /api/users端点（自动数据验证）",
                "自动生成GET /api/users/{id}端点",
                "自动生成PUT /api/users/{id}端点",
                "自动生成DELETE /api/users/{id}端点",
                "自动处理分页逻辑",
                "自动处理搜索逻辑",
                "自动处理排序逻辑",
                "自动处理数据验证",
                "自动处理异常"
            ],
            "code_lines": "只需要1行代码：app.add_auto_api(User)",
            "savings": "减少95%的CRUD代码"
        })
    
    # 注册所有路由
    app.include_router(test_router)
    app.include_router(exception_router)
    app.include_router(crud_router)
    
    # ================== 添加根路径 ==================
    @app.get("/")
    async def root():
        """根路径 - PyAdvanceKit 封装功能测试"""
        return success_response({
            "message": "PyAdvanceKit FastAPI 封装功能测试",
            "description": "测试 PyAdvanceKit 如何封装和增强 FastAPI 功能",
            "version": "1.0.0",
            "test_endpoints": {
                "overview": "/api/test - 测试概览",
                "response_format": "/api/test/response-format - 响应格式测试",
                "middleware": "/api/test/middleware-test - 中间件测试",
                "performance": "/api/test/performance-test - 性能测试",
                "config": "/api/test/config-test - 配置测试",
                "crud_comparison": "/api/crud-test - CRUD操作对比",
                "exception_test": "/api/exception-test - 异常处理测试"
            },
            "auto_generated_apis": {
                "users": "/api/users - 自动生成的用户管理API",
                "products": "/api/products - 自动生成的产品管理API（支持软删除）"
            },
            "documentation": {
                "swagger": "/docs - Swagger API文档",
                "redoc": "/redoc - ReDoc API文档"
            },
            "pyadvincekit_advantages": {
                "开发效率": "减少80%的重复代码",
                "代码质量": "统一的架构和最佳实践",
                "维护成本": "标准化的错误处理和日志记录",
                "学习成本": "开箱即用，无需学习复杂配置"
            }
        })
    
    print("✅ PyAdvanceKit 封装功能测试应用创建完成！")
    return app


# ================== 创建应用实例 ==================

# 创建测试应用
app = create_pyadvincekit_test_app()


# ================== 启动函数 ==================

async def startup():
    """应用启动时的初始化"""
    print("🗄️ 初始化数据库...")
    await init_database()
    print("✅ 数据库初始化完成")
    print()
    print("🎉 PyAdvanceKit 封装功能测试应用启动成功！")
    print("=" * 60)
    print("🌐 访问地址:")
    print("   📚 API文档: http://localhost:8000/docs")
    print("   📖 ReDoc文档: http://localhost:8000/redoc")
    print("   🏠 首页: http://localhost:8000/")
    print("   🧪 功能测试: http://localhost:8000/api/test/")
    print()
    print("🔗 PyAdvanceKit 自动生成的API端点:")
    print("   👥 用户管理: http://localhost:8000/api/users")
    print("   📦 产品管理: http://localhost:8000/api/products")
    print()
    print("🧪 测试端点:")
    print("   📋 测试概览: http://localhost:8000/api/test/")
    print("   📄 响应格式: http://localhost:8000/api/test/response-format")
    print("   🔧 中间件: http://localhost:8000/api/test/middleware-test")
    print("   ⚡ 性能: http://localhost:8000/api/test/performance-test")
    print("   ⚙️ 配置: http://localhost:8000/api/test/config-test")
    print("   🔄 CRUD对比: http://localhost:8000/api/crud-test/")
    print("   ❌ 异常处理: http://localhost:8000/api/exception-test/")
    print()
    print("💡 PyAdvanceKit 封装功能测试:")
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


# 添加生命周期事件处理器
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    """应用生命周期管理"""
    # 启动时执行
    await startup()
    yield
    # 关闭时执行（如果需要的话）
    print("🔄 应用正在关闭...")


# ================== 主函数 ==================

def main():
    """主函数 - 启动 PyAdvanceKit 封装功能测试应用"""
    import uvicorn
    
    print("🚀 启动 PyAdvanceKit 封装功能测试应用...")
    print("=" * 60)
    print("📝 这个应用专门测试 PyAdvanceKit 如何封装和增强 FastAPI 功能")
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
