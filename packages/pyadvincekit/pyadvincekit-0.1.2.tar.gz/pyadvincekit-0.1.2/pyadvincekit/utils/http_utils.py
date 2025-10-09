#!/usr/bin/env python3
"""
HTTP通讯工具类

提供HTTP请求、响应处理的便捷功能
"""

import asyncio
import json
import ssl
from typing import Dict, Any, Optional, Union, List, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
import aiohttp
import requests
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pyadvincekit.logging import get_logger

logger = get_logger(__name__)


class HTTPClient:
    """HTTP客户端工具类"""
    
    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        verify_ssl: bool = True,
        headers: Optional[Dict[str, str]] = None
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl
        self.default_headers = headers or {}
        
        # 设置默认请求头
        self.default_headers.setdefault("User-Agent", "PyAdvanceKit-HTTPClient/1.0")
        self.default_headers.setdefault("Content-Type", "application/json")
    
    def _prepare_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """准备请求头"""
        final_headers = self.default_headers.copy()
        if headers:
            final_headers.update(headers)
        return final_headers
    
    def _prepare_url(self, base_url: str, path: str = "") -> str:
        """准备完整URL"""
        if not path:
            return base_url
        return urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
    
    # 同步HTTP方法
    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """同步GET请求"""
        session = self._create_sync_session()
        final_headers = self._prepare_headers(headers)
        
        try:
            response = session.get(
                url,
                params=params,
                headers=final_headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
                **kwargs
            )
            logger.info(f"GET {url} -> {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"GET {url} failed: {e}")
            raise
    
    def post(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """同步POST请求"""
        session = self._create_sync_session()
        final_headers = self._prepare_headers(headers)
        
        try:
            response = session.post(
                url,
                data=data,
                json=json_data,
                headers=final_headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
                **kwargs
            )
            logger.info(f"POST {url} -> {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"POST {url} failed: {e}")
            raise
    
    def put(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """同步PUT请求"""
        session = self._create_sync_session()
        final_headers = self._prepare_headers(headers)
        
        try:
            response = session.put(
                url,
                data=data,
                json=json_data,
                headers=final_headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
                **kwargs
            )
            logger.info(f"PUT {url} -> {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"PUT {url} failed: {e}")
            raise
    
    def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """同步DELETE请求"""
        session = self._create_sync_session()
        final_headers = self._prepare_headers(headers)
        
        try:
            response = session.delete(
                url,
                headers=final_headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
                **kwargs
            )
            logger.info(f"DELETE {url} -> {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"DELETE {url} failed: {e}")
            raise
    
    def _create_sync_session(self) -> requests.Session:
        """创建同步会话"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    # 异步HTTP方法
    async def async_get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """异步GET请求"""
        final_headers = self._prepare_headers(headers)
        
        async with self._create_async_session() as session:
            try:
                async with session.get(
                    url,
                    params=params,
                    headers=final_headers,
                    **kwargs
                ) as response:
                    logger.info(f"ASYNC GET {url} -> {response.status}")
                    
                    # 读取响应内容
                    try:
                        response_data = await response.json()
                    except Exception:
                        response_data = await response.text()
                    
                    # 返回标准化的响应格式
                    return {
                        "status_code": response.status,
                        "data": response_data,
                        "headers": dict(response.headers),
                        "content": response_data,
                        "json": lambda: response_data if isinstance(response_data, dict) else {}
                    }
            except Exception as e:
                logger.error(f"ASYNC GET {url} failed: {e}")
                raise
    
    async def async_post(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """异步POST请求"""
        final_headers = self._prepare_headers(headers)
        
        async with self._create_async_session() as session:
            try:
                async with session.post(
                    url,
                    data=data,
                    json=json_data,
                    headers=final_headers,
                    **kwargs
                ) as response:
                    logger.info(f"ASYNC POST {url} -> {response.status}")
                    
                    # 读取响应内容
                    try:
                        response_data = await response.json()
                    except Exception:
                        response_data = await response.text()
                    
                    # 返回标准化的响应格式
                    return {
                        "status_code": response.status,
                        "data": response_data,
                        "headers": dict(response.headers),
                        "content": response_data,
                        "json": lambda: response_data if isinstance(response_data, dict) else {}
                    }
            except Exception as e:
                logger.error(f"ASYNC POST {url} failed: {e}")
                raise
    
    async def async_put(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """异步PUT请求"""
        final_headers = self._prepare_headers(headers)
        
        async with self._create_async_session() as session:
            try:
                async with session.put(
                    url,
                    data=data,
                    json=json_data,
                    headers=final_headers,
                    **kwargs
                ) as response:
                    logger.info(f"ASYNC PUT {url} -> {response.status}")
                    
                    # 读取响应内容
                    try:
                        response_data = await response.json()
                    except Exception:
                        response_data = await response.text()
                    
                    # 返回标准化的响应格式
                    return {
                        "status_code": response.status,
                        "data": response_data,
                        "headers": dict(response.headers),
                        "content": response_data,
                        "json": lambda: response_data if isinstance(response_data, dict) else {}
                    }
            except Exception as e:
                logger.error(f"ASYNC PUT {url} failed: {e}")
                raise
    
    async def async_delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """异步DELETE请求"""
        final_headers = self._prepare_headers(headers)
        
        async with self._create_async_session() as session:
            try:
                async with session.delete(
                    url,
                    headers=final_headers,
                    **kwargs
                ) as response:
                    logger.info(f"ASYNC DELETE {url} -> {response.status}")
                    
                    # 读取响应内容
                    try:
                        response_data = await response.json()
                    except Exception:
                        response_data = await response.text()
                    
                    # 返回标准化的响应格式
                    return {
                        "status_code": response.status,
                        "data": response_data,
                        "headers": dict(response.headers),
                        "content": response_data,
                        "json": lambda: response_data if isinstance(response_data, dict) else {}
                    }
            except Exception as e:
                logger.error(f"ASYNC DELETE {url} failed: {e}")
                raise
    
    def _create_async_session(self) -> ClientSession:
        """创建异步会话"""
        timeout = ClientTimeout(total=self.timeout)
        connector = TCPConnector(
            verify_ssl=self.verify_ssl,
            limit=100,  # 连接池大小
            limit_per_host=30
        )
        
        return ClientSession(
            timeout=timeout,
            connector=connector
        )


class HTTPUtils:
    """HTTP工具类"""
    
    @staticmethod
    def parse_url(url: str) -> Dict[str, Any]:
        """解析URL"""
        parsed = urlparse(url)
        return {
            "scheme": parsed.scheme,
            "netloc": parsed.netloc,
            "hostname": parsed.hostname,
            "port": parsed.port,
            "path": parsed.path,
            "params": parsed.params,
            "query": parsed.query,
            "fragment": parsed.fragment,
            "query_dict": parse_qs(parsed.query)
        }
    
    @staticmethod
    def build_query_string(params: Dict[str, Any]) -> str:
        """构建查询字符串"""
        from urllib.parse import urlencode
        return urlencode(params)
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """验证URL格式"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """提取域名"""
        try:
            return urlparse(url).netloc
        except:
            return None
    
    @staticmethod
    def is_json_response(response: requests.Response) -> bool:
        """判断响应是否为JSON格式"""
        content_type = response.headers.get("Content-Type", "")
        return "application/json" in content_type.lower()
    
    @staticmethod
    def safe_json_decode(text: str) -> Optional[Dict[str, Any]]:
        """安全解析JSON"""
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return None
    
    @staticmethod
    def get_response_size(response: requests.Response) -> int:
        """获取响应大小(字节)"""
        return len(response.content)
    
    @staticmethod
    def format_response_info(response: requests.Response) -> Dict[str, Any]:
        """格式化响应信息"""
        return {
            "status_code": response.status_code,
            "status_text": response.reason,
            "headers": dict(response.headers),
            "size": HTTPUtils.get_response_size(response),
            "encoding": response.encoding,
            "url": response.url,
            "elapsed_ms": response.elapsed.total_seconds() * 1000,
            "is_json": HTTPUtils.is_json_response(response)
        }


class APIClient:
    """API客户端基类"""
    
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        verify_ssl: bool = True
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        self.http_client = HTTPClient(
            timeout=timeout,
            verify_ssl=verify_ssl,
            headers=headers
        )
    
    def get(self, path: str, **kwargs) -> requests.Response:
        """GET请求"""
        url = self.http_client._prepare_url(self.base_url, path)
        return self.http_client.get(url, **kwargs)
    
    def post(self, path: str, **kwargs) -> requests.Response:
        """POST请求"""
        url = self.http_client._prepare_url(self.base_url, path)
        return self.http_client.post(url, **kwargs)
    
    def put(self, path: str, **kwargs) -> requests.Response:
        """PUT请求"""
        url = self.http_client._prepare_url(self.base_url, path)
        return self.http_client.put(url, **kwargs)
    
    def delete(self, path: str, **kwargs) -> requests.Response:
        """DELETE请求"""
        url = self.http_client._prepare_url(self.base_url, path)
        return self.http_client.delete(url, **kwargs)
    
    async def async_get(self, path: str, **kwargs) -> aiohttp.ClientResponse:
        """异步GET请求"""
        url = self.http_client._prepare_url(self.base_url, path)
        return await self.http_client.async_get(url, **kwargs)
    
    async def async_post(self, path: str, **kwargs) -> aiohttp.ClientResponse:
        """异步POST请求"""
        url = self.http_client._prepare_url(self.base_url, path)
        return await self.http_client.async_post(url, **kwargs)
    
    async def async_put(self, path: str, **kwargs) -> aiohttp.ClientResponse:
        """异步PUT请求"""
        url = self.http_client._prepare_url(self.base_url, path)
        return await self.http_client.async_put(url, **kwargs)
    
    async def async_delete(self, path: str, **kwargs) -> aiohttp.ClientResponse:
        """异步DELETE请求"""
        url = self.http_client._prepare_url(self.base_url, path)
        return await self.http_client.async_delete(url, **kwargs)


# 便捷函数
def create_http_client(**kwargs) -> HTTPClient:
    """创建HTTP客户端"""
    return HTTPClient(**kwargs)


def create_api_client(base_url: str, **kwargs) -> APIClient:
    """创建API客户端"""
    return APIClient(base_url, **kwargs)




