"""
    全局异常处理机制，捕获常见异常（如404、500、自定义业务异常），并返回结构化错误信息

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
import uvicorn

# 配置日志
logger = get_logger(__name__)


def demo_global_exception_handling():
    """演示：全局异常处理"""
    print("🛡️ 演示4：全局异常处理")
    print("=" * 50)

    app = create_app(title="全局异常处理演示")

    # 创建测试路由
    exception_router = APIRouter(prefix="/api/exception", tags=["异常处理"])

    @exception_router.get("/validation-error")
    async def validation_error():
        """测试验证错误"""
        raise CustomValidationError("数据验证失败", field="username")

    @exception_router.get("/not-found-error")
    async def not_found_error():
        """测试资源不存在错误"""
        raise NotFoundError("用户不存在", resource_type="User", resource_id="123")


    @exception_router.get("/http-error")
    async def http_error():
        """测试HTTP错误"""
        raise HTTPException(status_code=403, detail="禁止访问")


    @exception_router.get("/inter-error")
    async def http_error():
        """数据计算错误"""
        s = 1 / 0
        return success_response(
        data={"message": "操作成功", "timestamp": "2024-01-01T00:00:00Z"},
        message="请求处理成功"
    )

    @exception_router.get("/server-error")
    async def server_error():
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


if __name__ == '__main__':
    app = demo_global_exception_handling()
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=4000)
