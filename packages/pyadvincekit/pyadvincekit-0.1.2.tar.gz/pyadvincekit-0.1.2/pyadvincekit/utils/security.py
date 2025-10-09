"""
安全工具模块

提供加密、解密、哈希等安全相关的工具函数。
"""

import hashlib
import hmac
import secrets
import base64
from typing import Union, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SecurityUtils:
    """安全工具类"""
    
    @staticmethod
    def generate_secret_key(length: int = 32) -> str:
        """生成安全密钥"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_random_string(length: int = 16) -> str:
        """生成随机字符串"""
        return secrets.token_hex(length)
    
    @staticmethod
    def generate_random_bytes(length: int = 32) -> bytes:
        """生成随机字节"""
        return secrets.token_bytes(length)
    
    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> tuple[str, str]:
        """
        哈希密码
        
        Args:
            password: 明文密码
            salt: 盐值（可选）
            
        Returns:
            (哈希后的密码, 盐值的base64编码)
        """
        if salt is None:
            salt = secrets.token_bytes(32)
        
        # 使用PBKDF2进行密码哈希
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        password_hash = kdf.derive(password.encode('utf-8'))
        
        return (
            base64.b64encode(password_hash).decode('utf-8'),
            base64.b64encode(salt).decode('utf-8')
        )
    
    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: str) -> bool:
        """
        验证密码
        
        Args:
            password: 明文密码
            hashed_password: 哈希后的密码
            salt: 盐值
            
        Returns:
            密码是否匹配
        """
        try:
            salt_bytes = base64.b64decode(salt.encode('utf-8'))
            stored_hash = base64.b64decode(hashed_password.encode('utf-8'))
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt_bytes,
                iterations=100000,
            )
            
            # 验证密码
            kdf.verify(password.encode('utf-8'), stored_hash)
            return True
        except Exception:
            return False
    
    @staticmethod
    def md5_hash(data: Union[str, bytes]) -> str:
        """MD5哈希"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.md5(data).hexdigest()
    
    @staticmethod
    def sha256_hash(data: Union[str, bytes]) -> str:
        """SHA256哈希"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def sha512_hash(data: Union[str, bytes]) -> str:
        """SHA512哈希"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha512(data).hexdigest()
    
    @staticmethod
    def hmac_sha256(data: Union[str, bytes], key: Union[str, bytes]) -> str:
        """HMAC-SHA256签名"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        signature = hmac.new(key, data, hashlib.sha256)
        return signature.hexdigest()
    
    @staticmethod
    def verify_hmac_sha256(data: Union[str, bytes], key: Union[str, bytes], signature: str) -> bool:
        """验证HMAC-SHA256签名"""
        expected_signature = SecurityUtils.hmac_sha256(data, key)
        return hmac.compare_digest(expected_signature, signature)


class SymmetricEncryption:
    """对称加密工具"""
    
    def __init__(self, key: Optional[bytes] = None):
        """
        初始化加密器
        
        Args:
            key: 加密密钥（32字节），如果不提供则自动生成
        """
        if key is None:
            key = Fernet.generate_key()
        elif isinstance(key, str):
            # 如果是字符串，转换为密钥
            key = self._derive_key_from_password(key)
        
        self.key = key
        self.cipher = Fernet(key)
    
    @staticmethod
    def _derive_key_from_password(password: str, salt: Optional[bytes] = None) -> bytes:
        """从密码派生密钥"""
        if salt is None:
            salt = b"stable_salt_for_key_derivation"  # 在实际使用中应该使用随机盐
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        加密数据
        
        Args:
            data: 要加密的数据
            
        Returns:
            加密后的base64编码字符串
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted_data = self.cipher.encrypt(data)
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        解密数据
        
        Args:
            encrypted_data: 加密的base64编码字符串
            
        Returns:
            解密后的字符串
        """
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        decrypted_data = self.cipher.decrypt(encrypted_bytes)
        return decrypted_data.decode('utf-8')
    
    def get_key(self) -> str:
        """获取密钥的base64编码"""
        return base64.b64encode(self.key).decode('utf-8')


# 便捷函数
def generate_secret_key(length: int = 32) -> str:
    """生成安全密钥"""
    return SecurityUtils.generate_secret_key(length)


def generate_random_string(length: int = 16) -> str:
    """生成随机字符串"""
    return SecurityUtils.generate_random_string(length)


def hash_password(password: str) -> tuple[str, str]:
    """哈希密码"""
    return SecurityUtils.hash_password(password)


def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """验证密码"""
    return SecurityUtils.verify_password(password, hashed_password, salt)


def md5_hash(data: Union[str, bytes]) -> str:
    """MD5哈希"""
    return SecurityUtils.md5_hash(data)


def sha256_hash(data: Union[str, bytes]) -> str:
    """SHA256哈希"""
    return SecurityUtils.sha256_hash(data)


def encrypt_data(data: Union[str, bytes], password: str) -> str:
    """加密数据"""
    cipher = SymmetricEncryption(password)
    return cipher.encrypt(data)


def decrypt_data(encrypted_data: str, password: str) -> str:
    """解密数据"""
    cipher = SymmetricEncryption(password)
    return cipher.decrypt(encrypted_data)












