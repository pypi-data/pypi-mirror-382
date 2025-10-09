"""
    演示 fastapi 封装后， 自动注册 ，自动生成 CRUD 接口功能

"""

from pyadvincekit import (
    create_app, BaseModel, SoftDeleteModel, BaseCRUD, init_database
)
import uvicorn
from pyadvincekit.models.base import create_required_string_column, create_boolean_column,create_integer_column
from typing import Optional
from sqlalchemy.orm import Mapped
from users import User


# class User(BaseModel):
#     __tablename__ = "users"
#
#     username: Mapped[str] = create_required_string_column(50, unique=True, comment="用户名")
#     email: Mapped[str] = create_required_string_column(255, unique=True, comment="邮箱地址")
#     full_name: Mapped[str] = create_required_string_column(100, comment="全名")
#     age: Mapped[Optional[int]] = create_integer_column(comment="年龄", nullable=True)
#     is_active: Mapped[bool] = create_boolean_column(default=True, comment="是否激活")


app = create_app(
    title="自动 API 生成演示",
    description="演示 PyAdvanceKit 自动 API 生成功能",
    version="1.0.0"
)

# 自动生成用户管理 API
app.add_auto_api(
    model_class=User,
    router_prefix="/api/users",
    tags=["用户管理"]
)

if __name__ == '__main__':
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=8000)