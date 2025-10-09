"""
    统一响应报文格式：
        支持成功/失败状态封装

"""
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
import uvicorn

app = create_app(
        title="PyAdvanceKit 封装功能测试",
        description="测试 PyAdvanceKit 如何封装和增强 FastAPI 功能",
        version="1.0.0"
    )

# 添加测试路由
test_router = APIRouter(prefix="/api/test", tags=["PyAdvanceKit 封装测试"])


@test_router.get("/success")
async def success_test():
    """测试成功响应"""
    return success_response(
        data={"message": "操作成功", "timestamp": "2024-01-01T00:00:00Z"},
        message="请求处理成功"
    )


@test_router.get("/error")
async def error_test():
    """测试错误响应"""
    return error_response(
        message="这是一个测试错误",
        ret_code=ResponseCode.BAD_REQUEST,
        details={"field": "test_field", "reason": "validation_failed"}
    )


@test_router.get("/paginated")
async def paginated_test():
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

# 注册所有路由
app.include_router(test_router)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=3000)
