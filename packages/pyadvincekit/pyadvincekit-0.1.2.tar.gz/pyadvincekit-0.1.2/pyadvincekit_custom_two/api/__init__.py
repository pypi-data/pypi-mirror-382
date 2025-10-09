#!/usr/bin/env python3
"""
API 路由层

提供 FastAPI 路由和接口定义
"""

# 导入所有路由
from .acct_book_auto import acct_book_auto_router
from .acct_book_manual import acct_book_manual_router

__all__ = [
    "acct_book_auto_router",
    "acct_book_manual_router",
]
