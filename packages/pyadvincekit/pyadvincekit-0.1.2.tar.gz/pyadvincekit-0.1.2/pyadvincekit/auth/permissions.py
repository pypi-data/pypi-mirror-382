"""
权限系统

提供基于角色的访问控制(RBAC)功能。
"""

from enum import Enum
from typing import List, Set, Optional, Callable, Any
from functools import wraps

from fastapi import Request, HTTPException

from pyadvincekit.core.exceptions import AuthorizationError
from pyadvincekit.logging import get_logger

logger = get_logger(__name__)


class Permission(str, Enum):
    """权限枚举"""
    
    # 用户权限
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    
    # 管理员权限
    ADMIN_READ = "admin:read"
    ADMIN_WRITE = "admin:write"
    ADMIN_DELETE = "admin:delete"
    
    # 系统权限
    SYSTEM_CONFIG = "system:config"
    SYSTEM_MONITOR = "system:monitor"
    
    # 自定义权限
    CUSTOM_ACTION = "custom:action"


class Role:
    """角色类"""
    
    def __init__(self, name: str, permissions: Set[Permission]):
        self.name = name
        self.permissions = permissions
    
    def has_permission(self, permission: Permission) -> bool:
        """检查角色是否有指定权限"""
        return permission in self.permissions
    
    def add_permission(self, permission: Permission) -> None:
        """添加权限"""
        self.permissions.add(permission)
    
    def remove_permission(self, permission: Permission) -> None:
        """移除权限"""
        self.permissions.discard(permission)


# 预定义角色
ROLES = {
    "guest": Role("guest", set()),
    "user": Role("user", {
        Permission.USER_READ,
    }),
    "admin": Role("admin", {
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_DELETE,
        Permission.ADMIN_READ,
        Permission.ADMIN_WRITE,
    }),
    "super_admin": Role("super_admin", {
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_DELETE,
        Permission.ADMIN_READ,
        Permission.ADMIN_WRITE,
        Permission.ADMIN_DELETE,
        Permission.SYSTEM_CONFIG,
        Permission.SYSTEM_MONITOR,
    }),
}


class PermissionChecker:
    """权限检查器"""
    
    def __init__(self, user_role_provider: Optional[Callable] = None):
        """
        初始化权限检查器
        
        Args:
            user_role_provider: 用户角色提供者函数，接收用户ID返回角色列表
        """
        self.user_role_provider = user_role_provider or self._default_role_provider
    
    def _default_role_provider(self, user_id: str) -> List[str]:
        """默认角色提供者（返回普通用户角色）"""
        return ["user"]
    
    def check_permission(self, user_id: str, required_permission: Permission) -> bool:
        """
        检查用户是否有指定权限
        
        Args:
            user_id: 用户ID
            required_permission: 所需权限
            
        Returns:
            是否有权限
        """
        try:
            user_roles = self.user_role_provider(user_id)
            
            for role_name in user_roles:
                role = ROLES.get(role_name)
                if role and role.has_permission(required_permission):
                    logger.debug(f"User {user_id} has permission {required_permission} via role {role_name}")
                    return True
            
            logger.warning(f"User {user_id} lacks permission {required_permission}")
            return False
            
        except Exception as e:
            logger.error(f"Error checking permission for user {user_id}: {e}")
            return False
    
    def check_any_permission(self, user_id: str, permissions: List[Permission]) -> bool:
        """检查用户是否有任一指定权限"""
        return any(self.check_permission(user_id, perm) for perm in permissions)
    
    def check_all_permissions(self, user_id: str, permissions: List[Permission]) -> bool:
        """检查用户是否有所有指定权限"""
        return all(self.check_permission(user_id, perm) for perm in permissions)
    
    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """获取用户的所有权限"""
        permissions = set()
        user_roles = self.user_role_provider(user_id)
        
        for role_name in user_roles:
            role = ROLES.get(role_name)
            if role:
                permissions.update(role.permissions)
        
        return permissions


# 全局权限检查器实例
_permission_checker: Optional[PermissionChecker] = None


def get_permission_checker() -> PermissionChecker:
    """获取权限检查器实例"""
    global _permission_checker
    if _permission_checker is None:
        _permission_checker = PermissionChecker()
    return _permission_checker


def set_user_role_provider(provider: Callable[[str], List[str]]) -> None:
    """设置用户角色提供者"""
    global _permission_checker
    _permission_checker = PermissionChecker(provider)


# 便捷函数
def check_permission(user_id: str, permission: Permission) -> bool:
    """检查权限（便捷函数）"""
    checker = get_permission_checker()
    return checker.check_permission(user_id, permission)


def require_permission(permission: Permission):
    """权限要求装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从参数中查找Request对象
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # 从kwargs中查找
                request = kwargs.get('request')
            
            if not request or not hasattr(request.state, 'user_id'):
                raise HTTPException(status_code=401, detail="Authentication required")
            
            user_id = request.state.user_id
            if not check_permission(user_id, permission):
                raise HTTPException(
                    status_code=403, 
                    detail=f"Permission denied: {permission} required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(permissions: List[Permission]):
    """任一权限要求装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request or not hasattr(request.state, 'user_id'):
                raise HTTPException(status_code=401, detail="Authentication required")
            
            user_id = request.state.user_id
            checker = get_permission_checker()
            
            if not checker.check_any_permission(user_id, permissions):
                permission_names = [p.value for p in permissions]
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: one of {permission_names} required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role_name: str):
    """角色要求装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request or not hasattr(request.state, 'user_id'):
                raise HTTPException(status_code=401, detail="Authentication required")
            
            user_id = request.state.user_id
            checker = get_permission_checker()
            user_roles = checker.user_role_provider(user_id)
            
            if role_name not in user_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Role denied: {role_name} role required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# 权限管理函数
def add_role(name: str, permissions: Set[Permission]) -> None:
    """添加新角色"""
    ROLES[name] = Role(name, permissions)
    logger.info(f"Added new role: {name}")


def get_role(name: str) -> Optional[Role]:
    """获取角色"""
    return ROLES.get(name)


def list_roles() -> List[str]:
    """列出所有角色"""
    return list(ROLES.keys())


def list_permissions() -> List[Permission]:
    """列出所有权限"""
    return list(Permission)
