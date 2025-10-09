"""
数据验证工具模块

提供常用的数据验证函数。
"""

import re
from typing import Any, List, Optional, Union
from email_validator import validate_email as _validate_email, EmailNotValidError


class ValidationError(Exception):
    """验证错误异常"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)


class Validators:
    """验证器工具类"""
    
    # 正则表达式模式
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^1[3-9]\d{9}$')  # 中国手机号
    ID_CARD_PATTERN = re.compile(r'^\d{17}[\dXx]$')  # 中国身份证号
    PASSWORD_STRONG_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    IPV4_PATTERN = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    
    @staticmethod
    def is_email(email: str, check_deliverability: bool = True) -> bool:
        """
        验证邮箱地址
        
        Args:
            email: 邮箱地址
            check_deliverability: 是否检查可投递性
            
        Returns:
            是否为有效邮箱
        """
        try:
            # 尝试使用 check_deliverability 参数
            try:
                _validate_email(email, check_deliverability=check_deliverability)
            except TypeError:
                # 如果参数不支持，则使用默认调用
                _validate_email(email)
            return True
        except EmailNotValidError:
            return False
    
    @staticmethod
    def is_phone(phone: str, country: str = 'CN') -> bool:
        """
        验证手机号
        
        Args:
            phone: 手机号
            country: 国家代码
            
        Returns:
            是否为有效手机号
        """
        if country == 'CN':
            return bool(Validators.PHONE_PATTERN.match(phone))
        else:
            # 简单的国际手机号验证
            return len(phone) >= 10 and phone.replace('+', '').replace('-', '').replace(' ', '').isdigit()
    
    @staticmethod
    def is_id_card(id_card: str, country: str = 'CN') -> bool:
        """
        验证身份证号
        
        Args:
            id_card: 身份证号
            country: 国家代码
            
        Returns:
            是否为有效身份证号
        """
        if country == 'CN':
            if not Validators.ID_CARD_PATTERN.match(id_card):
                return False
            
            # 校验位验证
            weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
            check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
            
            sum_val = sum(int(id_card[i]) * weights[i] for i in range(17))
            check_code = check_codes[sum_val % 11]
            
            return id_card[17].upper() == check_code
        else:
            # 其他国家的身份证验证需要具体实现
            return len(id_card) >= 5
    
    @staticmethod
    def is_strong_password(password: str) -> bool:
        """
        验证强密码
        
        Args:
            password: 密码
            
        Returns:
            是否为强密码
        """
        return bool(Validators.PASSWORD_STRONG_PATTERN.match(password))
    
    @staticmethod
    def is_url(url: str) -> bool:
        """
        验证URL
        
        Args:
            url: URL地址
            
        Returns:
            是否为有效URL
        """
        return bool(Validators.URL_PATTERN.match(url))
    
    @staticmethod
    def is_ipv4(ip: str) -> bool:
        """
        验证IPv4地址
        
        Args:
            ip: IP地址
            
        Returns:
            是否为有效IPv4地址
        """
        return bool(Validators.IPV4_PATTERN.match(ip))
    
    @staticmethod
    def is_in_range(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> bool:
        """
        验证数值范围
        
        Args:
            value: 数值
            min_val: 最小值
            max_val: 最大值
            
        Returns:
            是否在范围内
        """
        return min_val <= value <= max_val
    
    @staticmethod
    def is_length_valid(text: str, min_length: int = 0, max_length: Optional[int] = None) -> bool:
        """
        验证字符串长度
        
        Args:
            text: 字符串
            min_length: 最小长度
            max_length: 最大长度
            
        Returns:
            长度是否有效
        """
        length = len(text)
        if length < min_length:
            return False
        if max_length is not None and length > max_length:
            return False
        return True
    
    @staticmethod
    def is_numeric(value: str) -> bool:
        """
        验证是否为数字
        
        Args:
            value: 字符串值
            
        Returns:
            是否为数字
        """
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_integer(value: str) -> bool:
        """
        验证是否为整数
        
        Args:
            value: 字符串值
            
        Returns:
            是否为整数
        """
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_positive(value: Union[int, float]) -> bool:
        """
        验证是否为正数
        
        Args:
            value: 数值
            
        Returns:
            是否为正数
        """
        return value > 0
    
    @staticmethod
    def is_non_negative(value: Union[int, float]) -> bool:
        """
        验证是否为非负数
        
        Args:
            value: 数值
            
        Returns:
            是否为非负数
        """
        return value >= 0
    
    @staticmethod
    def is_in_list(value: Any, valid_values: List[Any]) -> bool:
        """
        验证值是否在列表中
        
        Args:
            value: 值
            valid_values: 有效值列表
            
        Returns:
            是否在列表中
        """
        return value in valid_values
    
    @staticmethod
    def is_alpha(text: str) -> bool:
        """
        验证是否只包含字母
        
        Args:
            text: 字符串
            
        Returns:
            是否只包含字母
        """
        return text.isalpha()
    
    @staticmethod
    def is_alphanumeric(text: str) -> bool:
        """
        验证是否只包含字母和数字
        
        Args:
            text: 字符串
            
        Returns:
            是否只包含字母和数字
        """
        return text.isalnum()
    
    @staticmethod
    def contains_only(text: str, allowed_chars: str) -> bool:
        """
        验证字符串是否只包含指定字符
        
        Args:
            text: 字符串
            allowed_chars: 允许的字符
            
        Returns:
            是否只包含指定字符
        """
        return all(char in allowed_chars for char in text)


class DataValidator:
    """数据验证器"""
    
    def __init__(self):
        self.errors = []
    
    def validate_email(self, email: str, field_name: str = "email") -> "DataValidator":
        """验证邮箱"""
        if not Validators.is_email(email):
            self.errors.append(f"{field_name}: 无效的邮箱地址")
        return self
    
    def validate_phone(self, phone: str, field_name: str = "phone") -> "DataValidator":
        """验证手机号"""
        if not Validators.is_phone(phone):
            self.errors.append(f"{field_name}: 无效的手机号")
        return self
    
    def validate_required(self, value: Any, field_name: str) -> "DataValidator":
        """验证必填项"""
        if value is None or (isinstance(value, str) and not value.strip()):
            self.errors.append(f"{field_name}: 字段不能为空")
        return self
    
    def validate_length(
        self, 
        text: str, 
        min_length: int = 0, 
        max_length: Optional[int] = None, 
        field_name: str = "field"
    ) -> "DataValidator":
        """验证字符串长度"""
        if not Validators.is_length_valid(text, min_length, max_length):
            if max_length:
                self.errors.append(f"{field_name}: 长度必须在 {min_length} 到 {max_length} 之间")
            else:
                self.errors.append(f"{field_name}: 长度必须大于等于 {min_length}")
        return self
    
    def validate_range(
        self, 
        value: Union[int, float], 
        min_val: Union[int, float], 
        max_val: Union[int, float], 
        field_name: str = "field"
    ) -> "DataValidator":
        """验证数值范围"""
        if not Validators.is_in_range(value, min_val, max_val):
            self.errors.append(f"{field_name}: 值必须在 {min_val} 到 {max_val} 之间")
        return self
    
    def validate_url(self, url: str, field_name: str = "url") -> "DataValidator":
        """验证URL"""
        if not Validators.is_url(url):
            self.errors.append(f"{field_name}: 无效的URL地址")
        return self
    
    def validate_password_strength(self, password: str, field_name: str = "password") -> "DataValidator":
        """验证密码强度"""
        if not Validators.is_strong_password(password):
            self.errors.append(f"{field_name}: 密码必须包含大小写字母、数字和特殊字符，且长度至少8位")
        return self
    
    def is_valid(self) -> bool:
        """检查是否通过所有验证"""
        return len(self.errors) == 0
    
    def get_errors(self) -> List[str]:
        """获取所有错误信息"""
        return self.errors.copy()
    
    def clear_errors(self) -> "DataValidator":
        """清除错误信息"""
        self.errors.clear()
        return self
    
    def raise_if_invalid(self) -> None:
        """如果验证失败则抛出异常"""
        if not self.is_valid():
            raise ValidationError("; ".join(self.errors))


# 便捷函数
def validate_email(email: str, check_deliverability: bool = False) -> bool:
    """验证邮箱地址"""
    return Validators.is_email(email, check_deliverability)


def validate_phone(phone: str, country: str = 'CN') -> bool:
    """验证手机号"""
    return Validators.is_phone(phone, country)


def validate_url(url: str) -> bool:
    """验证URL"""
    return Validators.is_url(url)


def validate_password_strength(password: str) -> bool:
    """验证密码强度"""
    return Validators.is_strong_password(password)


def create_validator() -> DataValidator:
    """创建数据验证器"""
    return DataValidator()
