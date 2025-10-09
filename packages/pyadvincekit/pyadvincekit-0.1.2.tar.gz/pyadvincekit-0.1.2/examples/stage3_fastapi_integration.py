"""
阶段三：FastAPI集成示例

演示 PyAdvanceKit 的 FastAPI 集成功能：
- FastAPI应用工厂
- 统一响应格式
- 全局异常处理
- 中间件集成
- 路由自动注册
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel as PydanticModel

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pyadvincekit import (
    # 应用工厂
    create_app, FastAPIAppFactory,
    # 数据库
    BaseModel, BaseCRUD, get_database, init_database,
    # 响应格式
    success_response, error_response, paginated_response,
    ResponseCode, ResponseMessage,
    # 中间件
    setup_all_middleware,
    # 配置
    Settings
)
from pyadvincekit.models.base import create_required_string_column
from pyadvincekit.core.exceptions import ValidationError as CustomValidationError, NotFoundError


# ================== 数据模型 ==================

class User(BaseModel):
    """用户模型"""
    __tablename__ = "api_users"
    
    username: Mapped[str] = create_required_string_column(50, unique=True, comment="用户名")
    email: Mapped[str] = create_required_string_column(255, unique=True, comment="邮箱")
    full_name: Mapped[str] = create_required_string_column(100, comment="全名")
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="年龄")


# ================== Pydantic模型 ==================

class UserCreate(PydanticModel):
    """用户创建模型"""
    username: str
    email: str
    full_name: str
    age: Optional[int] = None


class UserUpdate(PydanticModel):
    """用户更新模型"""
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    age: Optional[int] = None


class UserResponse(PydanticModel):
    """用户响应模型"""
    id: str
    username: str
    email: str
    full_name: str
    age: Optional[int]
    created_at: str
    updated_at: str


# ================== CRUD服务 ==================

class UserService:
    """用户服务"""
    
    def __init__(self):
        self.crud = BaseCRUD(User)
    
    async def create_user(self, user_data: UserCreate) -> User:
        """创建用户"""
        # 数据验证
        async with get_database() as db:
            # 检查用户名是否已存在
            existing_users = await self.crud.get_multi(
                db, filters={"username": user_data.username}
            )
            if existing_users:
                raise ValidationError("用户名已存在", field="username")
            
            # 检查邮箱是否已存在
            existing_emails = await self.crud.get_multi(
                db, filters={"email": user_data.email}
            )
            if existing_emails:
                raise ValidationError("邮箱已被使用", field="email")
            
            return await self.crud.create(db, user_data.model_dump())
    
    async def get_user(self, user_id: str) -> User:
        """获取用户"""
        async with get_database() as db:
            user = await self.crud.get(db, user_id, raise_not_found=False)
            if not user:
                raise NotFoundError(f"用户不存在", resource_type="用户", resource_id=user_id)
            return user
    
    async def get_users(self, skip: int = 0, limit: int = 20) -> tuple[List[User], int]:
        """获取用户列表"""
        async with get_database() as db:
            users = await self.crud.get_multi(db, skip=skip, limit=limit)
            total = await self.crud.count(db)
            return users, total
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> User:
        """更新用户"""
        async with get_database() as db:
            user = await self.crud.get(db, user_id, raise_not_found=False)
            if not user:
                raise NotFoundError(f"用户不存在", resource_type="用户", resource_id=user_id)
            
            # 只更新提供的字段
            update_data = user_data.model_dump(exclude_unset=True)
            return await self.crud.update(db, user, update_data)
    
    async def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        async with get_database() as db:
            user = await self.crud.get(db, user_id, raise_not_found=False)
            if not user:
                raise NotFoundError(f"用户不存在", resource_type="用户", resource_id=user_id)
            
            return await self.crud.delete(db, user_id)


# ================== API路由 ==================

user_service = UserService()
user_router = APIRouter(prefix="/users", tags=["用户管理"])


@user_router.post("/", response_model=dict)
async def create_user(user_data: UserCreate):
    """创建用户"""
    user = await user_service.create_user(user_data)
    user_dict = user.to_dict()
    return success_response(user_dict, ResponseMessage.CREATED)


@user_router.get("/{user_id}", response_model=dict)
async def get_user(user_id: str):
    """获取用户详情"""
    user = await user_service.get_user(user_id)
    user_dict = user.to_dict()
    return success_response(user_dict, ResponseMessage.QUERIED)


@user_router.get("/", response_model=dict)
async def get_users(skip: int = 0, limit: int = 20):
    """获取用户列表"""
    users, total = await user_service.get_users(skip, limit)
    
    # 转换为字典列表
    user_dicts = [user.to_dict() for user in users]
    
    # 返回分页响应
    page = (skip // limit) + 1
    return paginated_response(
        items=user_dicts,
        page=page,
        page_size=limit,
        total=total,
        message=ResponseMessage.QUERIED
    )


@user_router.put("/{user_id}", response_model=dict)
async def update_user(user_id: str, user_data: UserUpdate):
    """更新用户"""
    user = await user_service.update_user(user_id, user_data)
    user_dict = user.to_dict()
    return success_response(user_dict, ResponseMessage.UPDATED)


@user_router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: str):
    """删除用户"""
    success = await user_service.delete_user(user_id)
    return success_response({"deleted": success}, ResponseMessage.DELETED)


# 测试路由
test_router = APIRouter(prefix="/test", tags=["测试"])


@test_router.get("/success")
async def test_success():
    """测试成功响应"""
    return success_response({"message": "这是一个成功的响应"})


@test_router.get("/error")
async def test_error():
    """测试错误响应"""
    raise CustomValidationError("这是一个测试错误", field="test_field")


@test_router.get("/http-error")
async def test_http_error():
    """测试HTTP错误"""
    raise HTTPException(status_code=404, detail="这是一个HTTP错误")


@test_router.get("/server-error")
async def test_server_error():
    """测试服务器错误"""
    raise Exception("这是一个未处理的异常")


# ================== 应用配置和创建 ==================

def example_basic_app():
    """基础应用创建示例"""
    print("=== 基础应用创建示例 ===")
    
    # 方式一：使用便捷函数创建
    app = create_app(
        title="PyAdvanceKit API 示例",
        description="展示 PyAdvanceKit 的 FastAPI 集成功能",
        version="1.0.0",
        routers=[user_router, test_router]
    )
    
    print(f"应用创建成功: {app.title}")
    print(f"文档地址: {app.docs_url}")
    print(f"包含路由: {len(app.routes)} 个")
    print()
    
    return app


def example_advanced_app():
    """高级应用创建示例"""
    print("=== 高级应用创建示例 ===")
    
    # 自定义配置
    settings = Settings(
        app_name="高级API应用",
        environment="development",
        debug=True,
        api_prefix="/api/v2"
    )
    
    # 方式二：使用工厂类创建
    factory = FastAPIAppFactory(settings)
    
    # 添加路由
    factory.add_router(user_router)
    factory.add_router(test_router)
    
    # 添加自定义中间件
    def custom_middleware(app):
        from starlette.middleware.base import BaseHTTPMiddleware
        
        class CustomMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                print(f"自定义中间件: {request.method} {request.url}")
                response = await call_next(request)
                return response
        
        app.add_middleware(CustomMiddleware)
        print("自定义中间件已添加")
    
    factory.add_middleware(custom_middleware)
    
    # 添加启动回调
    def startup_callback():
        print("应用启动回调被调用")
    
    factory.add_startup_callback(startup_callback)
    
    # 创建应用
    app = factory.create_app(
        title="高级PyAdvanceKit API",
        description="使用工厂模式创建的高级应用",
        version="2.0.0"
    )
    
    print(f"高级应用创建成功: {app.title}")
    print()
    
    return app


def example_middleware_configuration():
    """中间件配置示例"""
    print("=== 中间件配置示例 ===")
    
    # 创建基础应用
    app = create_app(title="中间件测试应用")
    
    # 添加所有推荐的中间件
    setup_all_middleware(app)
    
    print("所有中间件已配置:")
    print("- 请求ID中间件")
    print("- 请求日志中间件") 
    print("- 性能监控中间件")
    print("- 安全头中间件")
    print()
    
    return app


async def example_api_testing():
    """API测试示例"""
    print("=== API测试示例 ===")
    
    # 模拟API调用
    print("1. 创建用户")
    try:
        user_data = UserCreate(
            username="test_user",
            email="test@example.com",
            full_name="测试用户",
            age=25
        )
        user = await user_service.create_user(user_data)
        print(f"   ✅ 用户创建成功: {user.username}")
        
        # 获取用户
        print("2. 获取用户")
        retrieved_user = await user_service.get_user(user.id)
        print(f"   ✅ 用户获取成功: {retrieved_user.full_name}")
        
        # 更新用户
        print("3. 更新用户")
        update_data = UserUpdate(full_name="更新的用户名")
        updated_user = await user_service.update_user(user.id, update_data)
        print(f"   ✅ 用户更新成功: {updated_user.full_name}")
        
        # 获取用户列表
        print("4. 获取用户列表")
        users, total = await user_service.get_users()
        print(f"   ✅ 用户列表获取成功: 共 {total} 个用户")
        
        # 删除用户
        print("5. 删除用户")
        success = await user_service.delete_user(user.id)
        print(f"   ✅ 用户删除成功: {success}")
        
    except Exception as e:
        print(f"   ❌ API测试失败: {e}")
    
    print()


async def example_error_handling():
    """错误处理示例"""
    print("=== 错误处理示例 ===")
    
    try:
        # 测试验证错误
        print("1. 测试重复用户名错误")
        user_data = UserCreate(
            username="duplicate",
            email="duplicate1@example.com",
            full_name="重复用户1"
        )
        await user_service.create_user(user_data)
        
        # 尝试创建重复用户名
        user_data2 = UserCreate(
            username="duplicate",  # 重复用户名
            email="duplicate2@example.com",
            full_name="重复用户2"
        )
        await user_service.create_user(user_data2)
        
    except CustomValidationError as e:
        print(f"   ✅ 捕获验证错误: {e.message}")
    
    try:
        # 测试不存在的用户
        print("2. 测试用户不存在错误")
        await user_service.get_user("non-existent-id")
        
    except NotFoundError as e:
        print(f"   ✅ 捕获用户不存在错误: {e.message}")
    
    print()


async def main():
    """主函数"""
    print("🚀 PyAdvanceKit FastAPI集成示例")
    print("=" * 50)
    
    # 初始化数据库
    print("📊 初始化数据库...")
    await init_database()
    print("✅ 数据库初始化完成")
    print()
    
    # 运行所有示例
    app1 = example_basic_app()
    app2 = example_advanced_app()
    app3 = example_middleware_configuration()
    
    await example_api_testing()
    await example_error_handling()
    
    print("✅ FastAPI集成示例完成！")
    print("\n💡 提示:")
    print("1. 使用 create_app() 可以快速创建应用")
    print("2. 使用 FastAPIAppFactory 可以进行高级配置")
    print("3. 统一响应格式自动应用到所有端点")
    print("4. 全局异常处理自动处理各种错误")
    print("5. 中间件提供日志、性能监控等功能")
    print()
    print("🌐 启动应用示例:")
    print("   uvicorn main:app --reload")
    print("   然后访问 http://localhost:8000/docs 查看API文档")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ 运行失败: {e}")
        print("\n💡 可能的解决方案:")
        print("1. 安装异步插件: pip install pytest-asyncio")
        print("2. 或者直接运行: python -m asyncio examples.stage3_fastapi_integration")
        import traceback
        traceback.print_exc()
