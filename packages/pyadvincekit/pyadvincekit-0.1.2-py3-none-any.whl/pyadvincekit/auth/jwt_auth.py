"""
JWT认证模块

提供JWT令牌的生成、验证和用户认证功能。
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

try:
    import jwt
except ImportError:
    try:
        from jose import jwt
    except ImportError:
        raise ImportError("JWT library not found. Install with: pip install PyJWT or python-jose")
from passlib.context import CryptContext

from pyadvincekit.core.config import get_settings
from pyadvincekit.core.exceptions import AuthenticationError, ValidationError
from pyadvincekit.logging import get_logger

logger = get_logger(__name__)


class JWTAuth:
    """JWT认证类"""
    
    def __init__(self, settings=None):
        self.settings = settings or get_settings()
        self.secret_key = self.settings.jwt_secret_key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = self.settings.jwt_access_token_expire_minutes
        self.refresh_token_expire_days = self.settings.jwt_refresh_token_expire_days
        
        # 密码加密上下文
        # 智能选择密码哈希方案，避免 bcrypt 版本警告
        self.pwd_context = self._create_password_context()
    
    def _create_password_context(self) -> CryptContext:
        """
        创建密码加密上下文，智能选择最合适的哈希方案
        
        Returns:
            CryptContext: 密码加密上下文
        """
        # 方案优先级：pbkdf2_sha256 > sha256_crypt > bcrypt
        # 优先使用 pbkdf2_sha256 因为它更稳定，没有版本兼容性问题
        
        schemes = ["pbkdf2_sha256", "sha256_crypt"]
        
        # 只有在明确需要时才尝试 bcrypt
        if hasattr(self.settings, 'jwt_use_bcrypt') and self.settings.jwt_use_bcrypt:
            schemes.insert(0, "bcrypt")
        
        for scheme in schemes:
            try:
                context = CryptContext(schemes=[scheme], deprecated="auto")
                # 测试一下是否工作正常
                test_password = "test"
                hashed = context.hash(test_password)
                context.verify(test_password, hashed)
                return context
            except Exception:
                continue
        
        # 如果所有方案都失败，使用默认方案
        return CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    
    def create_access_token(
        self, 
        subject: Union[str, int], 
        expires_delta: Optional[timedelta] = None,
        extra_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        创建访问令牌
        
        Args:
            subject: 主体（通常是用户ID）
            expires_delta: 过期时间间隔
            extra_claims: 额外声明
            
        Returns:
            JWT访问令牌
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode = {
            "sub": str(subject),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        if extra_claims:
            to_encode.update(extra_claims)
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        logger.info(f"Created access token for subject: {subject}")
        return encoded_jwt
    
    def create_refresh_token(
        self, 
        subject: Union[str, int],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建刷新令牌
        
        Args:
            subject: 主体（通常是用户ID）
            expires_delta: 过期时间间隔
            
        Returns:
            JWT刷新令牌
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode = {
            "sub": str(subject),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        logger.info(f"Created refresh token for subject: {subject}")
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        验证令牌
        
        Args:
            token: JWT令牌
            token_type: 令牌类型（access或refresh）
            
        Returns:
            令牌载荷
            
        Raises:
            AuthenticationError: 令牌无效
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 检查令牌类型
            if payload.get("type") != token_type:
                raise AuthenticationError(f"Invalid token type, expected {token_type}")
            
            # 检查是否过期
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                raise AuthenticationError("Token has expired")
            
            logger.debug(f"Token verified successfully for subject: {payload.get('sub')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.JWTError as e:
            raise AuthenticationError(f"Invalid token: {e}")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """
        使用刷新令牌生成新的访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            新的访问令牌
        """
        payload = self.verify_token(refresh_token, "refresh")
        subject = payload.get("sub")
        
        if not subject:
            raise AuthenticationError("Invalid refresh token: missing subject")
        
        return self.create_access_token(subject)
    
    def hash_password(self, password: str) -> str:
        """
        哈希密码
        
        Args:
            password: 明文密码
            
        Returns:
            哈希后的密码
        """
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        验证密码
        
        Args:
            plain_password: 明文密码
            hashed_password: 哈希密码
            
        Returns:
            密码是否匹配
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_subject_from_token(self, token: str) -> str:
        """
        从令牌中获取主体
        
        Args:
            token: JWT令牌
            
        Returns:
            主体（用户ID）
        """
        payload = self.verify_token(token)
        subject = payload.get("sub")
        
        if not subject:
            raise AuthenticationError("Invalid token: missing subject")
        
        return subject


# 全局JWT认证实例
_jwt_auth: Optional[JWTAuth] = None


def get_jwt_auth() -> JWTAuth:
    """获取JWT认证实例"""
    global _jwt_auth
    if _jwt_auth is None:
        _jwt_auth = JWTAuth()
    return _jwt_auth


# 便捷函数
def create_access_token(
    subject: Union[str, int], 
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None
) -> str:
    """创建访问令牌（便捷函数）"""
    jwt_auth = get_jwt_auth()
    return jwt_auth.create_access_token(subject, expires_delta, extra_claims)


def create_refresh_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None
) -> str:
    """创建刷新令牌（便捷函数）"""
    jwt_auth = get_jwt_auth()
    return jwt_auth.create_refresh_token(subject, expires_delta)


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """验证令牌（便捷函数）"""
    jwt_auth = get_jwt_auth()
    return jwt_auth.verify_token(token, token_type)


def get_current_user(token: str) -> str:
    """从令牌获取当前用户（便捷函数）"""
    jwt_auth = get_jwt_auth()
    return jwt_auth.get_subject_from_token(token)
