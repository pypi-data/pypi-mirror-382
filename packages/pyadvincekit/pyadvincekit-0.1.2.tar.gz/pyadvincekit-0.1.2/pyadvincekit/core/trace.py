#!/usr/bin/env python3
"""
TraceId 跟踪模块

提供分布式链路跟踪功能，支持traceId的生成、传递和记录
"""

import uuid
import contextvars
import threading
from typing import Optional, Dict, Any, Callable
from datetime import datetime
import structlog
from functools import wraps

from pyadvincekit.logging import get_logger

logger = get_logger(__name__)

# 全局上下文变量
trace_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('trace_id')
span_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('span_id')
parent_span_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('parent_span_id')
user_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('user_id')
request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('request_id')

# 线程本地存储（用于同步代码）
_thread_local = threading.local()


class TraceContext:
    """跟踪上下文管理器"""
    
    def __init__(
        self,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        **extra_context
    ):
        # 如果有parent_span_id但没有trace_id，说明这是子跟踪，需要继承父跟踪的trace_id
        if parent_span_id is not None and trace_id is None:
            # 从当前上下文获取trace_id
            current_trace_id = TraceManager.get_current_trace_id()
            self.trace_id = current_trace_id or self.generate_trace_id()
        else:
            self.trace_id = trace_id or self.generate_trace_id()
        
        self.span_id = span_id or self.generate_span_id()
        self.parent_span_id = parent_span_id
        self.user_id = user_id
        self.request_id = request_id
        self.extra_context = extra_context
        self._old_trace_id = None
        self._old_span_id = None
        self._old_parent_span_id = None
        self._old_user_id = None
        self._old_request_id = None
    
    @staticmethod
    def generate_trace_id() -> str:
        """生成traceId"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_span_id() -> str:
        """生成spanId"""
        return str(uuid.uuid4())[:16]  # 使用16位短ID
    
    def __enter__(self):
        """进入上下文"""
        # 保存旧值
        try:
            self._old_trace_id = trace_id_var.get()
        except LookupError:
            self._old_trace_id = None
        
        try:
            self._old_span_id = span_id_var.get()
        except LookupError:
            self._old_span_id = None
        
        try:
            self._old_parent_span_id = parent_span_id_var.get()
        except LookupError:
            self._old_parent_span_id = None
        
        try:
            self._old_user_id = user_id_var.get()
        except LookupError:
            self._old_user_id = None
        
        try:
            self._old_request_id = request_id_var.get()
        except LookupError:
            self._old_request_id = None
        
        # 设置新值
        trace_id_var.set(self.trace_id)
        span_id_var.set(self.span_id)
        parent_span_id_var.set(self.parent_span_id)
        user_id_var.set(self.user_id)
        request_id_var.set(self.request_id)
        
        # 记录跟踪开始
        logger.info(
            "Trace context started",
            trace_id=self.trace_id,
            span_id=self.span_id,
            parent_span_id=self.parent_span_id,
            user_id=self.user_id,
            request_id=self.request_id,
            **self.extra_context
        )
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        # 记录跟踪结束
        if exc_type:
            logger.error(
                "Trace context ended with exception",
                trace_id=self.trace_id,
                span_id=self.span_id,
                exception_type=exc_type.__name__,
                exception_message=str(exc_val),
                **self.extra_context
            )
        else:
            logger.info(
                "Trace context ended successfully",
                trace_id=self.trace_id,
                span_id=self.span_id,
                **self.extra_context
            )
        
        # 恢复旧值
        trace_id_var.set(self._old_trace_id)
        span_id_var.set(self._old_span_id)
        parent_span_id_var.set(self._old_parent_span_id)
        user_id_var.set(self._old_user_id)
        request_id_var.set(self._old_request_id)


class TraceManager:
    """跟踪管理器"""
    
    @staticmethod
    def generate_trace_id() -> str:
        """生成traceId"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_span_id() -> str:
        """生成spanId"""
        return str(uuid.uuid4())[:16]  # 使用16位短ID
    
    @staticmethod
    def get_current_trace_id() -> Optional[str]:
        """获取当前traceId"""
        try:
            return trace_id_var.get()
        except LookupError:
            return None
    
    @staticmethod
    def get_current_span_id() -> Optional[str]:
        """获取当前spanId"""
        try:
            return span_id_var.get()
        except LookupError:
            return None
    
    @staticmethod
    def get_current_parent_span_id() -> Optional[str]:
        """获取当前父spanId"""
        try:
            return parent_span_id_var.get()
        except LookupError:
            return None
    
    @staticmethod
    def get_current_user_id() -> Optional[str]:
        """获取当前用户ID"""
        try:
            return user_id_var.get()
        except LookupError:
            return None
    
    @staticmethod
    def get_current_request_id() -> Optional[str]:
        """获取当前请求ID"""
        try:
            return request_id_var.get()
        except LookupError:
            return None
    
    @staticmethod
    def get_current_context() -> Dict[str, Any]:
        """获取当前跟踪上下文"""
        return {
            "trace_id": TraceManager.get_current_trace_id(),
            "span_id": TraceManager.get_current_span_id(),
            "parent_span_id": TraceManager.get_current_parent_span_id(),
            "user_id": TraceManager.get_current_user_id(),
            "request_id": TraceManager.get_current_request_id(),
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def set_trace_context(
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> None:
        """设置跟踪上下文"""
        if trace_id is not None:
            trace_id_var.set(trace_id)
        if span_id is not None:
            span_id_var.set(span_id)
        if parent_span_id is not None:
            parent_span_id_var.set(parent_span_id)
        if user_id is not None:
            user_id_var.set(user_id)
        if request_id is not None:
            request_id_var.set(request_id)
    
    @staticmethod
    def clear_trace_context() -> None:
        """清除跟踪上下文"""
        trace_id_var.set(None)
        span_id_var.set(None)
        parent_span_id_var.set(None)
        user_id_var.set(None)
        request_id_var.set(None)
    
    @staticmethod
    def create_child_span(
        operation_name: str,
        **extra_context
    ) -> TraceContext:
        """创建子span"""
        current_trace_id = TraceManager.get_current_trace_id()
        current_span_id = TraceManager.get_current_span_id()
        
        # 如果没有当前跟踪，创建新的
        if current_trace_id is None:
            return TraceContext(
                **extra_context
            )
        
        return TraceContext(
            trace_id=current_trace_id,  # 继承父trace
            parent_span_id=current_span_id,  # 当前span作为父span
            **extra_context
        )
    
    @staticmethod
    def start_trace(
        operation_name: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        **extra_context
    ) -> TraceContext:
        """开始新的跟踪"""
        return TraceContext(
            user_id=user_id,
            request_id=request_id,
            operation_name=operation_name,
            **extra_context
        )


def trace_function(
    operation_name: Optional[str] = None,
    **extra_context
):
    """函数跟踪装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with TraceManager.create_child_span(name, **extra_context):
                logger.info(
                    f"Function {name} started",
                    function=func.__name__,
                    module=func.__module__,
                    args_count=len(args),
                    kwargs_keys=list(kwargs.keys()),
                    **TraceManager.get_current_context()
                )
                
                try:
                    result = func(*args, **kwargs)
                    logger.info(
                        f"Function {name} completed successfully",
                        function=func.__name__,
                        **TraceManager.get_current_context()
                    )
                    return result
                except Exception as e:
                    logger.error(
                        f"Function {name} failed",
                        function=func.__name__,
                        exception_type=type(e).__name__,
                        exception_message=str(e),
                        **TraceManager.get_current_context()
                    )
                    raise
        
        return wrapper
    return decorator


def trace_method(
    operation_name: Optional[str] = None,
    **extra_context
):
    """方法跟踪装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            name = operation_name or f"{self.__class__.__name__}.{func.__name__}"
            
            with TraceManager.create_child_span(name, **extra_context):
                logger.info(
                    f"Method {name} started",
                    class_name=self.__class__.__name__,
                    method=func.__name__,
                    args_count=len(args),
                    kwargs_keys=list(kwargs.keys()),
                    **TraceManager.get_current_context()
                )
                
                try:
                    result = func(self, *args, **kwargs)
                    logger.info(
                        f"Method {name} completed successfully",
                        class_name=self.__class__.__name__,
                        method=func.__name__,
                        **TraceManager.get_current_context()
                    )
                    return result
                except Exception as e:
                    logger.error(
                        f"Method {name} failed",
                        class_name=self.__class__.__name__,
                        method=func.__name__,
                        exception_type=type(e).__name__,
                        exception_message=str(e),
                        **TraceManager.get_current_context()
                    )
                    raise
        
        return wrapper
    return decorator


class TraceMiddleware:
    """跟踪中间件"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """ASGI中间件实现"""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # 从请求头中提取跟踪信息
        headers = dict(scope.get("headers", []))
        trace_id = headers.get(b"x-trace-id", b"").decode("utf-8") or None
        span_id = headers.get(b"x-span-id", b"").decode("utf-8") or None
        parent_span_id = headers.get(b"x-parent-span-id", b"").decode("utf-8") or None
        user_id = headers.get(b"x-user-id", b"").decode("utf-8") or None
        request_id = headers.get(b"x-request-id", b"").decode("utf-8") or None
        
        # 设置跟踪上下文
        with TraceManager.start_trace(
            operation_name="http_request",
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            user_id=user_id,
            request_id=request_id,
            method=scope.get("method"),
            path=scope.get("path"),
            query_string=scope.get("query_string", b"").decode("utf-8")
        ):
            # 添加跟踪头到响应
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.extend([
                        (b"x-trace-id", TraceManager.get_current_trace_id().encode("utf-8")),
                        (b"x-span-id", TraceManager.get_current_span_id().encode("utf-8")),
                    ])
                    message["headers"] = headers
                await send(message)
            
            await self.app(scope, receive, send_wrapper)


# 便捷函数
def get_current_trace_id() -> Optional[str]:
    """获取当前traceId"""
    return TraceManager.get_current_trace_id()


def get_current_span_id() -> Optional[str]:
    """获取当前spanId"""
    return TraceManager.get_current_span_id()


def get_current_context() -> Dict[str, Any]:
    """获取当前跟踪上下文"""
    return TraceManager.get_current_context()


def start_trace(operation_name: str, **kwargs) -> TraceContext:
    """开始新的跟踪"""
    return TraceManager.start_trace(operation_name, **kwargs)


def create_child_span(operation_name: str, **kwargs) -> TraceContext:
    """创建子span"""
    return TraceManager.create_child_span(operation_name, **kwargs)
