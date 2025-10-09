"""
通用工具函数

提供常用的辅助函数，如UUID生成、时间处理等。
"""

import uuid
from datetime import datetime
from typing import Optional


def generate_uuid() -> str:
    """生成UUID字符串"""
    return str(uuid.uuid4())


def datetime_to_str(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """将datetime对象转换为字符串"""
    return dt.strftime(format_str)


def str_to_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """将字符串转换为datetime对象"""
    return datetime.strptime(date_str, format_str)


def safe_str(value: any, default: str = "") -> str:
    """安全地将任意值转换为字符串"""
    try:
        return str(value) if value is not None else default
    except Exception:
        return default


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断字符串到指定长度"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def is_empty(value: any) -> bool:
    """检查值是否为空"""
    if value is None:
        return True
    if isinstance(value, (str, list, dict, tuple, set)):
        return len(value) == 0
    return False


def deep_merge_dict(base_dict: dict, update_dict: dict) -> dict:
    """深度合并字典"""
    result = base_dict.copy()
    
    for key, value in update_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dict(result[key], value)
        else:
            result[key] = value
    
    return result

