#!/usr/bin/env python3
"""
多服务调用支持

提供服务间通信功能，支持同步和异步调用
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from functools import wraps

from pyadvincekit.logging import get_logger, get_current_trace_id
from pyadvincekit.utils import HTTPClient, APIClient, create_http_client, create_api_client

logger = get_logger(__name__)


class ServiceStatus(Enum):
    """服务状态"""
    HEALTHY = "healthy"      # 健康
    UNHEALTHY = "unhealthy" # 不健康
    UNKNOWN = "unknown"     # 未知


class CallType(Enum):
    """调用类型"""
    SYNC = "sync"           # 同步调用
    ASYNC = "async"         # 异步调用
    BATCH = "batch"         # 批量调用


@dataclass
class ServiceEndpoint:
    """服务端点信息"""
    service_name: str
    base_url: str
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_check: Optional[float] = None
    health_check_path: str = "/health"
    auth_token: Optional[str] = None
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}


@dataclass
class ServiceCall:
    """服务调用信息"""
    call_id: str
    service_name: str
    endpoint: str
    method: str = "POST"
    data: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    timeout: Optional[int] = None
    trace_id: Optional[str] = None
    created_at: float = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: str = "pending"
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
        if self.trace_id is None:
            self.trace_id = get_current_trace_id()


class ServiceRegistry:
    """服务注册中心"""
    
    def __init__(self):
        self.services: Dict[str, ServiceEndpoint] = {}
        self.call_history: List[ServiceCall] = []
        self._lock = asyncio.Lock()
    
    def register_service(
        self,
        service_name: str,
        base_url: str,
        timeout: int = 30,
        retry_count: int = 3,
        retry_delay: float = 1.0,
        health_check_path: str = "/health",
        auth_token: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> ServiceEndpoint:
        """注册服务"""
        endpoint = ServiceEndpoint(
            service_name=service_name,
            base_url=base_url,
            timeout=timeout,
            retry_count=retry_count,
            retry_delay=retry_delay,
            health_check_path=health_check_path,
            auth_token=auth_token,
            headers=headers or {}
        )
        
        self.services[service_name] = endpoint
        logger.info(f"Service registered: {service_name} at {base_url}")
        return endpoint
    
    def get_service(self, service_name: str) -> Optional[ServiceEndpoint]:
        """获取服务信息"""
        return self.services.get(service_name)
    
    def list_services(self) -> List[ServiceEndpoint]:
        """列出所有服务"""
        return list(self.services.values())
    
    def unregister_service(self, service_name: str) -> bool:
        """注销服务"""
        if service_name in self.services:
            del self.services[service_name]
            logger.info(f"Service unregistered: {service_name}")
            return True
        return False
    
    async def health_check(self, service_name: str) -> bool:
        """健康检查"""
        service = self.get_service(service_name)
        if not service:
            return False
        
        try:
            client = create_http_client()
            response = await client.get(
                f"{service.base_url}{service.health_check_path}",
                timeout=service.timeout,
                headers=service.headers
            )
            
            is_healthy = response.status_code == 200
            service.status = ServiceStatus.HEALTHY if is_healthy else ServiceStatus.UNHEALTHY
            service.last_check = time.time()
            
            return is_healthy
            
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            service.status = ServiceStatus.UNHEALTHY
            service.last_check = time.time()
            return False
    
    async def health_check_all(self) -> Dict[str, bool]:
        """检查所有服务健康状态"""
        results = {}
        tasks = []
        
        for service_name in self.services:
            tasks.append(self.health_check(service_name))
        
        if tasks:
            health_results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, service_name in enumerate(self.services):
                results[service_name] = health_results[i] if not isinstance(health_results[i], Exception) else False
        
        return results


class ServiceClient:
    """服务客户端"""
    
    def __init__(self, registry: Optional[ServiceRegistry] = None):
        self.registry = registry or ServiceRegistry()
        self.http_client = create_http_client()
        # API客户端在需要时创建，因为需要base_url
        self._api_client = None
    
    def register_service(
        self,
        service_name: str,
        base_url: str,
        **kwargs
    ) -> ServiceEndpoint:
        """注册服务"""
        return self.registry.register_service(service_name, base_url, **kwargs)
    
    async def call_service(
        self,
        service_name: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """调用服务"""
        service = self.registry.get_service(service_name)
        if not service:
            raise ValueError(f"Service not found: {service_name}")
        
        call_id = str(uuid.uuid4())
        call = ServiceCall(
            call_id=call_id,
            service_name=service_name,
            endpoint=endpoint,
            method=method,
            data=data,
            headers=headers,
            timeout=timeout or service.timeout,
            trace_id=trace_id or get_current_trace_id()
        )
        
        # 记录调用
        self.registry.call_history.append(call)
        
        try:
            call.started_at = time.time()
            call.status = "running"
            
            # 构建完整URL
            url = f"{service.base_url}{endpoint}"
            
            # 合并headers
            request_headers = service.headers.copy()
            if call.headers:
                request_headers.update(call.headers)
            
            # 添加认证
            if service.auth_token:
                request_headers["Authorization"] = f"Bearer {service.auth_token}"
            
            # 添加跟踪ID
            if call.trace_id:
                request_headers["X-Trace-Id"] = call.trace_id
            
            # 添加请求ID
            request_headers["X-Request-Id"] = call_id
            
            logger.info(f"Calling service: {service_name}{endpoint}")
            
            # 执行HTTP请求
            if method.upper() == "GET":
                response = await self.http_client.async_get(
                    url, headers=request_headers, timeout=call.timeout
                )
            elif method.upper() == "POST":
                response = await self.http_client.async_post(
                    url, json_data=data, headers=request_headers, timeout=call.timeout
                )
            elif method.upper() == "PUT":
                response = await self.http_client.async_put(
                    url, json_data=data, headers=request_headers, timeout=call.timeout
                )
            elif method.upper() == "DELETE":
                response = await self.http_client.async_delete(
                    url, headers=request_headers, timeout=call.timeout
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # 处理响应
            call.response = {
                "status_code": response["status_code"],
                "data": response["data"],
                "headers": response["headers"]
            }
            call.status = "completed"
            call.completed_at = time.time()
            
            logger.info(f"Service call completed: {service_name}{endpoint} - {response['status_code']}")
            
            return call.response
            
        except Exception as e:
            call.error = str(e)
            call.status = "failed"
            call.completed_at = time.time()
            
            logger.error(f"Service call failed: {service_name}{endpoint} - {e}")
            raise
    
    async def call_service_sync(
        self,
        service_name: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """同步调用服务"""
        return await self.call_service(
            service_name, endpoint, data, method="POST", **kwargs
        )
    
    async def batch_call_services(
        self,
        calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """批量调用服务"""
        tasks = []
        
        for call_config in calls:
            task = self.call_service(**call_config)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "call_config": calls[i]
                })
            else:
                processed_results.append({
                    "success": True,
                    "result": result,
                    "call_config": calls[i]
                })
        
        return processed_results
    
    def get_call_history(self, service_name: Optional[str] = None) -> List[ServiceCall]:
        """获取调用历史"""
        history = self.registry.call_history
        if service_name:
            history = [call for call in history if call.service_name == service_name]
        return history
    
    def get_service_stats(self, service_name: str) -> Dict[str, Any]:
        """获取服务统计信息"""
        calls = self.get_call_history(service_name)
        
        if not calls:
            return {"total_calls": 0}
        
        total_calls = len(calls)
        successful_calls = len([call for call in calls if call.status == "completed"])
        failed_calls = len([call for call in calls if call.status == "failed"])
        
        avg_response_time = 0
        if calls:
            completed_calls = [call for call in calls if call.completed_at and call.started_at]
            if completed_calls:
                response_times = [call.completed_at - call.started_at for call in completed_calls]
                avg_response_time = sum(response_times) / len(response_times)
        
        return {
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "success_rate": successful_calls / total_calls if total_calls > 0 else 0,
            "average_response_time": avg_response_time
        }


# 全局服务客户端实例
_service_client: Optional[ServiceClient] = None


def get_service_client() -> ServiceClient:
    """获取全局服务客户端实例"""
    global _service_client
    if _service_client is None:
        _service_client = ServiceClient()
    return _service_client


def register_service(
    service_name: str,
    base_url: str,
    **kwargs
) -> ServiceEndpoint:
    """注册服务"""
    client = get_service_client()
    return client.register_service(service_name, base_url, **kwargs)


async def call_service(
    service_name: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """调用服务"""
    client = get_service_client()
    return await client.call_service(service_name, endpoint, data, **kwargs)


async def batch_call_services(calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """批量调用服务"""
    client = get_service_client()
    return await client.batch_call_services(calls)


def get_service_stats(service_name: str) -> Dict[str, Any]:
    """获取服务统计信息"""
    client = get_service_client()
    return client.get_service_stats(service_name)


# 装饰器
def service_call(
    service_name: str,
    endpoint: str,
    method: str = "POST"
):
    """服务调用装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 执行原函数
            result = await func(*args, **kwargs)
            
            # 调用服务
            try:
                service_response = await call_service(
                    service_name=service_name,
                    endpoint=endpoint,
                    data=result,
                    method=method
                )
                return service_response
            except Exception as e:
                logger.error(f"Service call failed in decorator: {e}")
                raise
        
        return wrapper
    return decorator


def health_check_service(service_name: str) -> bool:
    """检查服务健康状态"""
    client = get_service_client()
    return asyncio.run(client.registry.health_check(service_name))


async def health_check_all_services() -> Dict[str, bool]:
    """检查所有服务健康状态"""
    client = get_service_client()
    return await client.registry.health_check_all()
