"""
身份认证授权模块

提供JWT认证、权限控制等功能。
"""

from pyadvincekit.auth.jwt_auth import (
    JWTAuth,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
)
from pyadvincekit.auth.middleware import (
    AuthMiddleware,
    setup_auth_middleware,
)
from pyadvincekit.auth.permissions import (
    Permission,
    require_permission,
    check_permission,
)

__all__ = [
    # JWT认证
    "JWTAuth",
    "create_access_token",
    "create_refresh_token", 
    "verify_token",
    "get_current_user",
    
    # 认证中间件
    "AuthMiddleware",
    "setup_auth_middleware",
    
    # 权限系统
    "Permission",
    "require_permission",
    "check_permission",
]












