"""
    编写基础中间件：
        请求日志，加请求id
        性能监控，记录方法执行时间，监控性能

"""
import asyncio
import sys
import time
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
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
import uvicorn

# 配置日志
logger = get_logger(__name__)

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

    setup_all_middleware(app)


    # 添加测试路由
    middleware_router = APIRouter(prefix="/api/middleware", tags=["中间件"])

    @middleware_router.get("/request-info")
    async def get_request_info(request: Request):
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


if __name__ == '__main__':
    app = demo_middleware_integration()
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=4000)
