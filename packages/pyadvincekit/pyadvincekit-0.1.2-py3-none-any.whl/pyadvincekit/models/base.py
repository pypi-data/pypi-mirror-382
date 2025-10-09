"""
PyAdvanceKit Base Models

提供数据模型的基础类和工具函数。
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Type, TypeVar, Union
from sqlalchemy import (
    Boolean, Column, DateTime, Integer, String, Text, 
    Numeric, JSON, func, text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import expression

# 创建基础声明类
Base = declarative_base()

# 类型变量
ModelType = TypeVar('ModelType', bound='BaseModel')

class TimestampMixin:
    """时间戳混入类"""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="创建时间"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )


class SoftDeleteMixin:
    """软删除混入类"""
    
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=expression.false(),
        comment="是否已删除"
    )
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="删除时间"
    )


class BaseModel(Base, TimestampMixin):
    """基础模型类
    
    提供所有模型的基础功能：
    - UUID 主键
    - 创建和更新时间戳
    - 字典转换方法
    - 基础查询方法
    """
    
    __abstract__ = True
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="主键ID"
    )
    
    def to_dict(self, exclude: Optional[list] = None) -> Dict[str, Any]:
        """转换为字典
        
        Args:
            exclude: 要排除的字段列表
            
        Returns:
            字典格式的模型数据
        """
        exclude = exclude or []
        result = {}
        
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                # 处理日期时间类型
                if isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                else:
                    result[column.name] = value
        
        return result
    
    def update_from_dict(self, data: Dict[str, Any], exclude: Optional[list] = None) -> None:
        """从字典更新模型
        
        Args:
            data: 要更新的数据字典
            exclude: 要排除的字段列表
        """
        exclude = exclude or ['id', 'created_at', 'updated_at']
        
        for key, value in data.items():
            if key not in exclude and hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def from_dict(cls: Type[ModelType], data: Dict[str, Any], exclude: Optional[list] = None) -> ModelType:
        """从字典创建模型实例
        
        Args:
            data: 创建模型的数据字典
            exclude: 要排除的字段列表
            
        Returns:
            创建的模型实例
        """
        exclude = exclude or ['created_at', 'updated_at']
        
        # 过滤掉排除的字段
        filtered_data = {
            key: value for key, value in data.items() 
            if key not in exclude and hasattr(cls, key)
        }
        
        return cls(**filtered_data)
    
    @classmethod
    def get_table_name(cls) -> str:
        """获取表名"""
        return cls.__tablename__
    
    @classmethod
    def get_primary_key(cls) -> str:
        """获取主键字段名"""
        return "id"
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<{self.__class__.__name__}(id={self.id})>"


class SoftDeleteModel(BaseModel, SoftDeleteMixin):
    """支持软删除的基础模型类
    
    继承自 BaseModel，增加软删除功能：
    - is_deleted 字段
    - deleted_at 字段
    - 软删除相关方法
    """
    
    __abstract__ = True
    
    def soft_delete(self) -> None:
        """软删除"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """恢复删除"""
        self.is_deleted = False
        self.deleted_at = None
    
    @property
    def is_active(self) -> bool:
        """是否活跃（未删除）"""
        return not self.is_deleted
    
    def to_dict(self, exclude: Optional[list] = None, include_deleted: bool = False) -> Dict[str, Any]:
        """转换为字典
        
        Args:
            exclude: 要排除的字段列表
            include_deleted: 是否包含删除相关字段
            
        Returns:
            字典格式的模型数据
        """
        exclude = exclude or []
        if not include_deleted:
            exclude.extend(['is_deleted', 'deleted_at'])
        
        return super().to_dict(exclude=exclude)


# 便捷的字段创建函数

def create_required_string_column(
    max_length: int = 255,
    comment: str = "",
    unique: bool = False,
    index: bool = False
) -> Mapped[str]:
    """创建必填字符串字段
    
    Args:
        max_length: 最大长度
        comment: 字段注释
        unique: 是否唯一
        index: 是否创建索引
        
    Returns:
        字符串字段映射
    """
    return mapped_column(
        String(max_length),
        nullable=False,
        unique=unique,
        index=index,
        comment=comment
    )


def create_optional_string_column(
    max_length: int = 255,
    comment: str = "",
    default: Optional[str] = None,
    unique: bool = False,
    index: bool = False
) -> Mapped[Optional[str]]:
    """创建可选字符串字段
    
    Args:
        max_length: 最大长度
        comment: 字段注释
        default: 默认值
        unique: 是否唯一
        index: 是否创建索引
        
    Returns:
        可选字符串字段映射
    """
    return mapped_column(
        String(max_length),
        nullable=True,
        default=default,
        unique=unique,
        index=index,
        comment=comment
    )


def create_text_column(
    comment: str = "",
    nullable: bool = True,
    default: Optional[str] = None
) -> Mapped[Optional[str]]:
    """创建文本字段
    
    Args:
        comment: 字段注释
        nullable: 是否可为空
        default: 默认值
        
    Returns:
        文本字段映射
    """
    return mapped_column(
        Text,
        nullable=nullable,
        default=default,
        comment=comment
    )


def create_integer_column(
    comment: str = "",
    nullable: bool = True,
    default: Optional[int] = None,
    index: bool = False
) -> Mapped[Optional[int]]:
    """创建整数字段
    
    Args:
        comment: 字段注释
        nullable: 是否可为空
        default: 默认值
        index: 是否创建索引
        
    Returns:
        整数字段映射
    """
    return mapped_column(
        Integer,
        nullable=nullable,
        default=default,
        index=index,
        comment=comment
    )


def create_boolean_column(
    comment: str = "",
    default: bool = False,
    nullable: bool = False
) -> Mapped[bool]:
    """创建布尔字段
    
    Args:
        comment: 字段注释
        default: 默认值
        nullable: 是否可为空
        
    Returns:
        布尔字段映射
    """
    return mapped_column(
        Boolean,
        nullable=nullable,
        default=default,
        server_default=text('true' if default else 'false'),
        comment=comment
    )


def create_datetime_column(
    comment: str = "",
    nullable: bool = True,
    default: Optional[datetime] = None,
    auto_now: bool = False,
    auto_now_add: bool = False
) -> Mapped[Optional[datetime]]:
    """创建日期时间字段
    
    Args:
        comment: 字段注释
        nullable: 是否可为空
        default: 默认值
        auto_now: 是否自动更新
        auto_now_add: 是否自动添加
        
    Returns:
        日期时间字段映射
    """
    kwargs = {
        'nullable': nullable,
        'comment': comment
    }
    
    if auto_now_add:
        kwargs['server_default'] = func.now()
    elif auto_now:
        kwargs['server_default'] = func.now()
        kwargs['onupdate'] = func.now()
    elif default:
        kwargs['default'] = default
    
    return mapped_column(DateTime(timezone=True), **kwargs)


def create_decimal_column(
    precision: int = 10,
    scale: int = 2,
    comment: str = "",
    nullable: bool = True,
    default: Optional[Union[int, float, str]] = None
) -> Mapped[Optional[Any]]:
    """创建十进制数字段
    
    Args:
        precision: 精度（总位数）
        scale: 标度（小数位数）
        comment: 字段注释
        nullable: 是否可为空
        default: 默认值
        
    Returns:
        十进制数字段映射
    """
    return mapped_column(
        Numeric(precision=precision, scale=scale),
        nullable=nullable,
        default=default,
        comment=comment
    )


def create_json_column(
    comment: str = "",
    nullable: bool = True,
    default: Optional[Dict[str, Any]] = None
) -> Mapped[Optional[Dict[str, Any]]]:
    """创建JSON字段
    
    Args:
        comment: 字段注释
        nullable: 是否可为空
        default: 默认值
        
    Returns:
        JSON字段映射
    """
    return mapped_column(
        JSON,
        nullable=nullable,
        default=default,
        comment=comment
    )


def create_uuid_column(
    comment: str = "",
    nullable: bool = True,
    default: Optional[str] = None,
    auto_generate: bool = False
) -> Mapped[Optional[str]]:
    """创建UUID字段
    
    Args:
        comment: 字段注释
        nullable: 是否可为空
        default: 默认值
        auto_generate: 是否自动生成UUID
        
    Returns:
        UUID字段映射
    """
    kwargs = {
        'nullable': nullable,
        'comment': comment
    }
    
    if auto_generate:
        kwargs['default'] = lambda: str(uuid.uuid4())
    elif default:
        kwargs['default'] = default
    
    return mapped_column(String(36), **kwargs)


def create_float_column(
    comment: str = "",
    nullable: bool = True,
    default: Optional[float] = None,
    index: bool = False
) -> Mapped[Optional[float]]:
    """创建浮点数字段
    
    Args:
        comment: 字段注释
        nullable: 是否可为空
        default: 默认值
        index: 是否创建索引
        
    Returns:
        浮点数字段映射
    """
    from sqlalchemy import Float
    return mapped_column(
        Float,
        nullable=nullable,
        default=default,
        index=index,
        comment=comment
    )


def create_bigint_column(
    comment: str = "",
    nullable: bool = True,
    default: Optional[int] = None,
    index: bool = False
) -> Mapped[Optional[int]]:
    """创建大整数字段
    
    Args:
        comment: 字段注释
        nullable: 是否可为空
        default: 默认值
        index: 是否创建索引
        
    Returns:
        大整数字段映射
    """
    from sqlalchemy import BigInteger
    return mapped_column(
        BigInteger,
        nullable=nullable,
        default=default,
        index=index,
        comment=comment
    )


def create_enum_column(
    enum_class: Type,
    comment: str = "",
    nullable: bool = True,
    default: Optional[Any] = None,
    index: bool = False
) -> Mapped[Optional[Any]]:
    """创建枚举字段
    
    Args:
        enum_class: 枚举类
        comment: 字段注释
        nullable: 是否可为空
        default: 默认值
        index: 是否创建索引
        
    Returns:
        枚举字段映射
    """
    from sqlalchemy import Enum
    return mapped_column(
        Enum(enum_class),
        nullable=nullable,
        default=default,
        index=index,
        comment=comment
    )


def create_date_column(
    comment: str = "",
    nullable: bool = True,
    default: Optional[Any] = None,
    auto_now_add: bool = False
) -> Mapped[Optional[Any]]:
    """创建日期字段（仅日期，不含时间）
    
    Args:
        comment: 字段注释
        nullable: 是否可为空
        default: 默认值
        auto_now_add: 是否自动添加当前日期
        
    Returns:
        日期字段映射
    """
    from sqlalchemy import Date, func
    
    kwargs = {
        'nullable': nullable,
        'comment': comment
    }
    
    if auto_now_add:
        kwargs['server_default'] = func.current_date()
    elif default:
        kwargs['default'] = default
    
    return mapped_column(Date, **kwargs)


def create_time_column(
    comment: str = "",
    nullable: bool = True,
    default: Optional[Any] = None
) -> Mapped[Optional[Any]]:
    """创建时间字段（仅时间，不含日期）
    
    Args:
        comment: 字段注释
        nullable: 是否可为空
        default: 默认值
        
    Returns:
        时间字段映射
    """
    from sqlalchemy import Time
    return mapped_column(
        Time,
        nullable=nullable,
        default=default,
        comment=comment
    )


def create_binary_column(
    max_length: Optional[int] = None,
    comment: str = "",
    nullable: bool = True
) -> Mapped[Optional[bytes]]:
    """创建二进制字段
    
    Args:
        max_length: 最大长度
        comment: 字段注释
        nullable: 是否可为空
        
    Returns:
        二进制字段映射
    """
    from sqlalchemy import LargeBinary, VARBINARY
    
    if max_length:
        column_type = VARBINARY(max_length)
    else:
        column_type = LargeBinary
    
    return mapped_column(
        column_type,
        nullable=nullable,
        comment=comment
    )


def create_email_column(
    comment: str = "邮箱地址",
    nullable: bool = True,
    unique: bool = False,
    index: bool = True
) -> Mapped[Optional[str]]:
    """创建邮箱字段
    
    Args:
        comment: 字段注释
        nullable: 是否可为空
        unique: 是否唯一
        index: 是否创建索引
        
    Returns:
        邮箱字段映射
    """
    return mapped_column(
        String(255),
        nullable=nullable,
        unique=unique,
        index=index,
        comment=comment
    )


def create_phone_column(
    comment: str = "手机号码",
    nullable: bool = True,
    unique: bool = False,
    index: bool = True
) -> Mapped[Optional[str]]:
    """创建手机号字段
    
    Args:
        comment: 字段注释
        nullable: 是否可为空
        unique: 是否唯一
        index: 是否创建索引
        
    Returns:
        手机号字段映射
    """
    return mapped_column(
        String(20),
        nullable=nullable,
        unique=unique,
        index=index,
        comment=comment
    )


def create_url_column(
    max_length: int = 2000,
    comment: str = "URL地址",
    nullable: bool = True,
    index: bool = False
) -> Mapped[Optional[str]]:
    """创建URL字段
    
    Args:
        max_length: 最大长度
        comment: 字段注释
        nullable: 是否可为空
        index: 是否创建索引
        
    Returns:
        URL字段映射
    """
    return mapped_column(
        String(max_length),
        nullable=nullable,
        index=index,
        comment=comment
    )


def create_status_column(
    comment: str = "状态",
    default: int = 1,
    nullable: bool = False,
    index: bool = True
) -> Mapped[int]:
    """创建状态字段（通常用于表示记录状态）
    
    Args:
        comment: 字段注释
        default: 默认值
        nullable: 是否可为空
        index: 是否创建索引
        
    Returns:
        状态字段映射
    """
    return mapped_column(
        Integer,
        nullable=nullable,
        default=default,
        index=index,
        comment=comment
    )


def create_sort_order_column(
    comment: str = "排序",
    default: int = 0,
    nullable: bool = False,
    index: bool = True
) -> Mapped[int]:
    """创建排序字段
    
    Args:
        comment: 字段注释
        default: 默认值
        nullable: 是否可为空
        index: 是否创建索引
        
    Returns:
        排序字段映射
    """
    return mapped_column(
        Integer,
        nullable=nullable,
        default=default,
        index=index,
        comment=comment
    )


def create_foreign_key_column(
    foreign_key: str,
    comment: str = "",
    nullable: bool = True,
    index: bool = True,
    ondelete: str = "SET NULL"
) -> Mapped[Optional[str]]:
    """创建外键字段
    
    Args:
        foreign_key: 外键引用 (如: "users.id")
        comment: 字段注释
        nullable: 是否可为空
        index: 是否创建索引
        ondelete: 删除时的行为
        
    Returns:
        外键字段映射
    """
    from sqlalchemy import ForeignKey
    return mapped_column(
        String(36),
        ForeignKey(foreign_key, ondelete=ondelete),
        nullable=nullable,
        index=index,
        comment=comment
    )


def create_version_column(
    comment: str = "版本号",
    default: int = 1,
    nullable: bool = False
) -> Mapped[int]:
    """创建版本字段（用于乐观锁）
    
    Args:
        comment: 字段注释
        default: 默认值
        nullable: 是否可为空
        
    Returns:
        版本字段映射
    """
    return mapped_column(
        Integer,
        nullable=nullable,
        default=default,
        comment=comment
    )