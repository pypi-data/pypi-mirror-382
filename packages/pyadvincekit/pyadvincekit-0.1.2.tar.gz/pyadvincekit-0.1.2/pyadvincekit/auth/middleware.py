"""
认证中间件

提供JWT认证中间件和相关工具。
"""

from typing import Callable, List, Optional, Set
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from pyadvincekit.auth.jwt_auth import get_jwt_auth, verify_token
from pyadvincekit.core.exceptions import AuthenticationError, AuthorizationError
from pyadvincekit.logging import get_logger

logger = get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件"""
    
    def __init__(
        self,
        app: FastAPI,
        exclude_paths: Optional[Set[str]] = None,
        require_auth_by_default: bool = False
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or {
            "/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"
        }
        self.require_auth_by_default = require_auth_by_default
        self.jwt_auth = get_jwt_auth()
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 检查是否需要跳过认证
        if self._should_skip_auth(request):
            return await call_next(request)
        
        # 提取和验证令牌
        token = self._extract_token(request)
        
        if token:
            try:
                payload = self.jwt_auth.verify_token(token)
                # 将用户信息添加到请求状态
                request.state.user_id = payload.get("sub")
                request.state.user_payload = payload
                request.state.authenticated = True
                
                logger.debug(f"User authenticated: {payload.get('sub')}")
                
            except AuthenticationError as e:
                logger.warning(f"Authentication failed: {e}")
                if self.require_auth_by_default:
                    raise HTTPException(status_code=401, detail=str(e))
                request.state.authenticated = False
        else:
            request.state.authenticated = False
            if self.require_auth_by_default:
                raise HTTPException(status_code=401, detail="Authentication required")
        
        return await call_next(request)
    
    def _should_skip_auth(self, request: Request) -> bool:
        """检查是否应该跳过认证"""
        return request.url.path in self.exclude_paths
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """从请求中提取JWT令牌"""
        # 从Authorization头提取
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # 移除"Bearer "前缀
        
        # 从查询参数提取（可选）
        token = request.query_params.get("token")
        if token:
            return token
        
        # 从Cookie提取（可选）
        token = request.cookies.get("access_token")
        if token:
            return token
        
        return None


# FastAPI依赖注入
security = HTTPBearer(auto_error=False)


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """获取当前用户（可选）"""
    if not credentials:
        return None
    
    try:
        jwt_auth = get_jwt_auth()
        payload = jwt_auth.verify_token(credentials.credentials)
        return payload.get("sub")
    except AuthenticationError:
        return None


def get_current_user_required(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """获取当前用户（必需）"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        jwt_auth = get_jwt_auth()
        payload = jwt_auth.verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user ID")
        
        return user_id
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))


def require_auth(func: Callable) -> Callable:
    """认证装饰器"""
    async def wrapper(*args, **kwargs):
        # 这里应该检查请求状态中的认证信息
        # 实际实现需要访问当前请求对象
        return await func(*args, **kwargs)
    return wrapper


def require_roles(roles: List[str]) -> Callable:
    """角色要求装饰器"""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # 实现角色检查逻辑
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# 中间件设置函数
def setup_auth_middleware(
    app: FastAPI, 
    exclude_paths: Optional[Set[str]] = None,
    require_auth_by_default: bool = False
) -> None:
    """设置认证中间件"""
    app.add_middleware(
        AuthMiddleware,
        exclude_paths=exclude_paths,
        require_auth_by_default=require_auth_by_default
    )
    logger.info("认证中间件已配置")


# 认证路由辅助函数
def create_login_endpoint(app: FastAPI, user_validator: Callable) -> None:
    """创建登录端点"""
    from pydantic import BaseModel
    
    class LoginRequest(BaseModel):
        username: str
        password: str
    
    class LoginResponse(BaseModel):
        access_token: str
        refresh_token: str
        token_type: str = "bearer"
    
    @app.post("/auth/login", response_model=LoginResponse)
    async def login(request: LoginRequest):
        """用户登录"""
        # 验证用户凭据
        user = await user_validator(request.username, request.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # 生成令牌
        jwt_auth = get_jwt_auth()
        access_token = jwt_auth.create_access_token(user.id)
        refresh_token = jwt_auth.create_refresh_token(user.id)
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )


def create_refresh_endpoint(app: FastAPI) -> None:
    """创建令牌刷新端点"""
    from pydantic import BaseModel
    
    class RefreshRequest(BaseModel):
        refresh_token: str
    
    class RefreshResponse(BaseModel):
        access_token: str
        token_type: str = "bearer"
    
    @app.post("/auth/refresh", response_model=RefreshResponse)
    async def refresh_token(request: RefreshRequest):
        """刷新访问令牌"""
        try:
            jwt_auth = get_jwt_auth()
            new_access_token = jwt_auth.refresh_access_token(request.refresh_token)
            
            return RefreshResponse(access_token=new_access_token)
        except AuthenticationError as e:
            raise HTTPException(status_code=401, detail=str(e))
