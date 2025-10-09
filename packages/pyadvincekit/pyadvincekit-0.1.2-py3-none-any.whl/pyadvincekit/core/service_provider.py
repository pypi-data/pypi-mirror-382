#!/usr/bin/env python3
"""
服务提供者模块

用于接收和处理来自其他服务的调用
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import uuid
from functools import wraps

from pyadvincekit.logging import get_logger, get_current_trace_id
from pyadvincekit.core.response import success_response, error_response

logger = get_logger(__name__)


class ServiceMethod(Enum):
    """服务方法类型"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


@dataclass
class ServiceHandler:
    """服务处理器"""
    method: ServiceMethod
    endpoint: str
    handler: Callable
    description: str = ""
    auth_required: bool = False
    rate_limit: Optional[int] = None  # 每分钟请求数限制


@dataclass
class ServiceRequest:
    """服务请求"""
    request_id: str
    service_name: str
    endpoint: str
    method: str
    data: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    trace_id: Optional[str] = None
    client_ip: Optional[str] = None
    received_at: float = None
    
    def __post_init__(self):
        if self.received_at is None:
            self.received_at = time.time()


@dataclass
class ServiceResponse:
    """服务响应"""
    request_id: str
    status_code: int
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None
    trace_id: Optional[str] = None


class ServiceProvider:
    """服务提供者"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.handlers: Dict[str, ServiceHandler] = {}
        self.request_history: List[ServiceRequest] = []
        self.response_history: List[ServiceResponse] = []
        self._rate_limits: Dict[str, List[float]] = {}  # 用于速率限制
    
    def register_handler(
        self,
        method: ServiceMethod,
        endpoint: str,
        handler: Callable,
        description: str = "",
        auth_required: bool = False,
        rate_limit: Optional[int] = None
    ) -> ServiceHandler:
        """注册服务处理器"""
        handler_key = f"{method.value}:{endpoint}"
        
        service_handler = ServiceHandler(
            method=method,
            endpoint=endpoint,
            handler=handler,
            description=description,
            auth_required=auth_required,
            rate_limit=rate_limit
        )
        
        self.handlers[handler_key] = service_handler
        logger.info(f"Handler registered: {method.value} {endpoint}")
        
        return service_handler
    
    def get_handler(self, method: str, endpoint: str) -> Optional[ServiceHandler]:
        """获取处理器"""
        handler_key = f"{method}:{endpoint}"
        return self.handlers.get(handler_key)
    
    def list_handlers(self) -> List[ServiceHandler]:
        """列出所有处理器"""
        return list(self.handlers.values())
    
    def _check_rate_limit(self, handler: ServiceHandler, client_ip: str) -> bool:
        """检查速率限制"""
        if not handler.rate_limit:
            return True
        
        current_time = time.time()
        minute_ago = current_time - 60
        
        # 获取该客户端的请求历史
        if client_ip not in self._rate_limits:
            self._rate_limits[client_ip] = []
        
        # 清理过期的请求记录
        self._rate_limits[client_ip] = [
            req_time for req_time in self._rate_limits[client_ip]
            if req_time > minute_ago
        ]
        
        # 检查是否超过限制
        if len(self._rate_limits[client_ip]) >= handler.rate_limit:
            return False
        
        # 记录当前请求
        self._rate_limits[client_ip].append(current_time)
        return True
    
    async def handle_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        client_ip: Optional[str] = None
    ) -> ServiceResponse:
        """处理服务请求"""
        request_id = str(uuid.uuid4())
        trace_id = headers.get("X-Trace-Id") if headers else get_current_trace_id()
        
        # 创建请求记录
        request = ServiceRequest(
            request_id=request_id,
            service_name=self.service_name,
            endpoint=endpoint,
            method=method,
            data=data,
            headers=headers,
            trace_id=trace_id,
            client_ip=client_ip
        )
        
        self.request_history.append(request)
        
        try:
            # 查找处理器
            handler = self.get_handler(method, endpoint)
            if not handler:
                return ServiceResponse(
                    request_id=request_id,
                    status_code=404,
                    error=f"Handler not found: {method} {endpoint}",
                    trace_id=trace_id
                )
            
            # 检查速率限制
            if client_ip and not self._check_rate_limit(handler, client_ip):
                return ServiceResponse(
                    request_id=request_id,
                    status_code=429,
                    error="Rate limit exceeded",
                    trace_id=trace_id
                )
            
            # 检查认证（简单实现）
            if handler.auth_required:
                auth_header = headers.get("Authorization") if headers else None
                if not auth_header or not auth_header.startswith("Bearer "):
                    return ServiceResponse(
                        request_id=request_id,
                        status_code=401,
                        error="Authentication required",
                        trace_id=trace_id
                    )
            
            logger.info(f"Handling request: {method} {endpoint} (ID: {request_id})")
            
            # 执行处理器
            start_time = time.time()
            
            if asyncio.iscoroutinefunction(handler.handler):
                result = await handler.handler(data or {})
            else:
                result = handler.handler(data or {})
            
            processing_time = time.time() - start_time
            
            # 创建响应
            response = ServiceResponse(
                request_id=request_id,
                status_code=200,
                data=result,
                processing_time=processing_time,
                trace_id=trace_id
            )
            
            self.response_history.append(response)
            
            logger.info(f"Request handled successfully: {request_id} ({processing_time:.3f}s)")
            
            return response
            
        except Exception as e:
            processing_time = time.time() - request.received_at
            
            error_response = ServiceResponse(
                request_id=request_id,
                status_code=500,
                error=str(e),
                processing_time=processing_time,
                trace_id=trace_id
            )
            
            self.response_history.append(error_response)
            
            logger.error(f"Request handling failed: {request_id} - {e}")
            
            return error_response
    
    def get_request_history(
        self, 
        limit: Optional[int] = None,
        endpoint: Optional[str] = None
    ) -> List[ServiceRequest]:
        """获取请求历史"""
        history = self.request_history
        if endpoint:
            history = [req for req in history if req.endpoint == endpoint]
        if limit:
            history = history[-limit:]
        return history
    
    def get_response_history(
        self,
        limit: Optional[int] = None,
        status_code: Optional[int] = None
    ) -> List[ServiceResponse]:
        """获取响应历史"""
        history = self.response_history
        if status_code:
            history = [resp for resp in history if resp.status_code == status_code]
        if limit:
            history = history[-limit:]
        return history
    
    def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        total_requests = len(self.request_history)
        total_responses = len(self.response_history)
        
        if total_responses == 0:
            return {
                "total_requests": total_requests,
                "total_responses": total_responses,
                "success_rate": 0,
                "average_processing_time": 0
            }
        
        successful_responses = len([resp for resp in self.response_history if resp.status_code < 400])
        success_rate = successful_responses / total_responses
        
        processing_times = [resp.processing_time for resp in self.response_history if resp.processing_time]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        return {
            "total_requests": total_requests,
            "total_responses": total_responses,
            "success_rate": success_rate,
            "average_processing_time": avg_processing_time,
            "handlers_count": len(self.handlers)
        }


# 装饰器
def service_endpoint(
    method: ServiceMethod,
    endpoint: str,
    description: str = "",
    auth_required: bool = False,
    rate_limit: Optional[int] = None
):
    """服务端点装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        # 注册处理器（需要在ServiceProvider实例中注册）
        wrapper._service_endpoint = {
            "method": method,
            "endpoint": endpoint,
            "description": description,
            "auth_required": auth_required,
            "rate_limit": rate_limit
        }
        
        return wrapper
    return decorator


def get_service_endpoint(
    method: ServiceMethod,
    endpoint: str,
    description: str = "",
    auth_required: bool = False,
    rate_limit: Optional[int] = None
):
    """获取服务端点装饰器（简化版本）"""
    return service_endpoint(method, endpoint, description, auth_required, rate_limit)


# 全局服务提供者实例
_service_providers: Dict[str, ServiceProvider] = {}


def get_service_provider(service_name: str) -> ServiceProvider:
    """获取服务提供者实例"""
    if service_name not in _service_providers:
        _service_providers[service_name] = ServiceProvider(service_name)
    return _service_providers[service_name]


def register_service_handler(
    service_name: str,
    method: ServiceMethod,
    endpoint: str,
    handler: Callable,
    **kwargs
) -> ServiceHandler:
    """注册服务处理器"""
    provider = get_service_provider(service_name)
    return provider.register_handler(method, endpoint, handler, **kwargs)


async def handle_service_request(
    service_name: str,
    method: str,
    endpoint: str,
    **kwargs
) -> ServiceResponse:
    """处理服务请求"""
    provider = get_service_provider(service_name)
    return await provider.handle_request(method, endpoint, **kwargs)


def get_service_stats(service_name: str) -> Dict[str, Any]:
    """获取服务统计信息"""
    provider = get_service_provider(service_name)
    return provider.get_service_stats()









