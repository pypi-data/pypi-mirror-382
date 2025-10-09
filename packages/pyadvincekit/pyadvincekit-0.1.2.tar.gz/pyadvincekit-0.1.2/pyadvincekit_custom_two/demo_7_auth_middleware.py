"""
    jwt 身份校验中间件

"""


import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Depends, HTTPException
from pyadvincekit import create_app
from pyadvincekit.core.middleware import setup_all_middleware
from pyadvincekit.auth import (
    AuthMiddleware, setup_auth_middleware,
    create_access_token, verify_token, JWTAuth,
    Permission, require_permission
)
from pyadvincekit.logging import get_logger
from pydantic import BaseModel
import uvicorn


logger = get_logger(__name__)

def demo_auth_enabled():
    """演示身份校验启用状态"""
    print("\n🔐 演示2: 身份校验启用状态")
    print("-" * 50)

    # 创建应用，启用身份校验
    app = create_app(
        title="Demo App - Auth Enabled",
        include_database_init=False
    )

    # 设置所有中间件，启用身份校验
    setup_all_middleware(
        app,
        enable_auth=True,
        exclude_paths={"/public", "/health", "/docs", "/redoc", "/openapi.json"},
        require_auth_by_default=True
    )

    @app.get("/public")
    async def public_endpoint():
        return {"message": "这是公开端点，无需身份校验"}

    @app.get("/protected")
    async def protected_endpoint():
        return {"message": "这是受保护端点，需要身份校验"}

    @app.get("/admin")
    @require_permission(Permission.ADMIN_READ)
    async def admin_endpoint():
        return {"message": "这是管理员端点，需要特定权限"}

    print("✅ 应用已创建 - 身份校验中间件已启用")
    print("🔒 受保护端点需要有效 JWT Token")
    print("👨‍💼 管理员端点需要特定权限")

    return app


def demo_jwt_token_generation():
    """演示 JWT Token 生成和验证"""
    print("\n🎫 演示3: JWT Token 生成和验证")
    print("-" * 50)

    # 创建 JWT 认证实例
    jwt_auth = JWTAuth()

    # 生成访问令牌
    # 生成访问令牌
    user_id = "user123"
    extra_claims = {
        "username": "demo_user",
        "email": "demo@example.com",
        "roles": ["user"]
    }

    access_token = jwt_auth.create_access_token(subject=user_id, extra_claims=extra_claims)
    print(f"✅ 生成访问令牌: {access_token[:50]}...")

    # 验证令牌
    try:
        payload = jwt_auth.verify_token(access_token)
        print(f"✅ 令牌验证成功: 用户ID = {payload.get('sub')}")
        print(f"   用户名: {payload.get('username')}")
        print(f"   邮箱: {payload.get('email')}")
    except Exception as e:
        print(f"❌ 令牌验证失败: {e}")




if __name__ == '__main__':
    app = demo_auth_enabled()
    # JWT 功能演示
    demo_jwt_token_generation()

    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=4001)




