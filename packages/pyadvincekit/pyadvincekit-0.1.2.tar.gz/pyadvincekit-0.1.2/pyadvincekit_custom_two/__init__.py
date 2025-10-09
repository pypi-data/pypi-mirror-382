#!/usr/bin/env python3
"""
PyAdvanceKit Custom Two

基于 PyAdvanceKit 框架的账务管理演示项目
"""

__version__ = "1.0.0"
__description__ = "PyAdvanceKit Custom Two - 账务管理演示"

# 设置项目根目录到 Python 路径（解决导包问题）
import sys
from pathlib import Path

project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 导出主要组件
try:
    from .services.acct_book_service import AcctBookService
    from .api.acct_book_auto import acct_book_auto_router
    from .api.acct_book_manual import acct_book_manual_router

    __all__ = [
        "AcctBookService",
        "acct_book_auto_router",
        "acct_book_manual_router",
    ]

except ImportError as e:
    # 如果导入失败，至少确保路径设置生效
    print(f"Warning: Some modules could not be imported: {e}")
    __all__ = []
