"""
日志模块

提供结构化日志配置和处理器。
"""

from pyadvincekit.logging.handlers import (
    setup_logging,
    get_logger,
    set_request_context,
    LoggingSetup,
    JSONFormatter,
    ColoredFormatter,
    RequestIDFilter,
)

# 第二阶段新增：跟踪功能
from pyadvincekit.core.trace import (
    TraceContext, TraceManager, TraceMiddleware,
    trace_function, trace_method,
    get_current_trace_id, get_current_span_id, get_current_context,
    start_trace, create_child_span
)

__all__ = [
    "setup_logging",
    "get_logger", 
    "set_request_context",
    "LoggingSetup",
    "JSONFormatter",
    "ColoredFormatter",
    "RequestIDFilter",
    
    # 跟踪功能
    "TraceContext", "TraceManager", "TraceMiddleware",
    "trace_function", "trace_method",
    "get_current_trace_id", "get_current_span_id", "get_current_context",
    "start_trace", "create_child_span",
]
