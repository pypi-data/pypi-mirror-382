#!/usr/bin/env python3
"""
PyAdvanceKit Custom Two - FastAPI 应用

基于 PyAdvanceKit 框架的账务管理系统演示应用
"""

import sys
from pathlib import Path

# 确保项目根目录在 Python 路径中（参考 PyAdvanceKit Admin 的做法）
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from pyadvincekit import (
    create_app, setup_all_middleware, init_database,
    get_logger
)

# 导入路由（使用绝对导入，因为已经设置了 project_root）
from api.acct_book_auto import acct_book_auto_router
from api.acct_book_manual import acct_book_manual_router

logger = get_logger(__name__)

# 创建 FastAPI 应用
app = create_app(
    title="PyAdvanceKit 账务管理系统",
    description="基于 PyAdvanceKit 框架的账务登记管理 API 演示",
    version="1.0.0"
    # docs_url 和 redoc_url 使用 PyAdvanceKit 的默认设置
)

# 设置中间件
setup_all_middleware(app)

# 注册路由
app.include_router(acct_book_auto_router)   # 自动生成的 CRUD 接口
app.include_router(acct_book_manual_router) # 手动定义的业务接口

if __name__ == "__main__":
    import uvicorn
    
    logger.info("启动 FastAPI 服务器...")
    # uvicorn.run(
    #     app,
    #     host="0.0.0.0",
    #     port=8000,
    #     reload=True,  # 开发模式下启用热重载
    #     log_level="info"
    # )

    uvicorn.run(app, host="0.0.0.0", port=8000)
