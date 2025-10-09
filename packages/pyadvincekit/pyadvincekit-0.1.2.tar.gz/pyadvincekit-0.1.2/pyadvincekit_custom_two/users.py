from pyadvincekit import (
    create_app, BaseModel, SoftDeleteModel, BaseCRUD, init_database
)
from sqlalchemy.orm import Mapped
from pyadvincekit.models.base import create_required_string_column, create_boolean_column,create_integer_column
from typing import Optional


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = create_required_string_column(50, unique=True, comment="用户名")
    email: Mapped[str] = create_required_string_column(255, unique=True, comment="邮箱地址")
    full_name: Mapped[str] = create_required_string_column(100, comment="全名")
    age: Mapped[Optional[int]] = create_integer_column(comment="年龄", nullable=True)
    is_active: Mapped[bool] = create_boolean_column(default=True, comment="是否激活")
