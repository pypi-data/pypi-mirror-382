"""
PyAdvanceKit .env 配置演示

演示如何在外部项目中使用 .env 文件配置 PyAdvanceKit
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径（仅用于演示）
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pyadvincekit import (
    create_app, 
    get_settings, 
    reload_settings,
    init_database,
    get_logger
)
from pyadvincekit.core.config import Settings


def demo_env_config():
    """演示 .env 配置的使用"""
    print("=== PyAdvanceKit .env 配置演示 ===")
    print()
    
    # 1. 检查 .env 文件是否存在
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print(f"✅ 发现 .env 文件: {env_file}")
    else:
        print(f"⚠️ 未发现 .env 文件: {env_file}")
        print("   请创建 .env 文件或使用 env_config_example.txt 作为模板")
        print()
        return
    
    # 2. 重新加载配置（确保读取最新的 .env 文件）
    print("🔄 重新加载配置...")
    settings = reload_settings()
    
    # 3. 显示当前配置
    print("📋 当前配置:")
    print(f"   应用名称: {settings.app_name}")
    print(f"   调试模式: {settings.debug}")
    print(f"   环境: {settings.environment}")
    print(f"   数据库URL: {settings.database.database_url}")
    print(f"   日志级别: {settings.logging.log_level}")
    print(f"   日志文件: {settings.logging.log_file_path}")
    print(f"   JWT密钥: {settings.jwt.secret_key[:20]}..." if settings.jwt.secret_key else "   未设置")
    print()
    
    # 4. 创建应用（使用 .env 配置）
    print("🚀 创建 FastAPI 应用...")
    app = create_app(
        title=settings.app_name,
        description="使用 .env 配置的 PyAdvanceKit 应用",
        version="1.0.0"
    )
    
    # 5. 添加测试路由
    @app.get("/")
    async def root():
        """根路径 - 显示配置信息"""
        return {
            "message": "PyAdvanceKit .env 配置演示",
            "config": {
                "app_name": settings.app_name,
                "environment": settings.environment,
                "debug": settings.debug,
                "database_url": settings.database.database_url,
                "log_level": settings.logging.log_level,
                "log_file": settings.logging.log_file_path
            },
            "note": "所有配置都来自 .env 文件"
        }
    
    @app.get("/config")
    async def get_config():
        """获取完整配置信息"""
        return {
            "app_config": {
                "app_name": settings.app_name,
                "debug": settings.debug,
                "environment": settings.environment
            },
            "database_config": {
                "database_url": settings.database.database_url,
                "pool_size": settings.database.pool_size,
                "max_overflow": settings.database.max_overflow
            },
            "logging_config": {
                "log_level": settings.logging.log_level,
                "log_file_enabled": settings.logging.log_file_enabled,
                "log_file_path": settings.logging.log_file_path,
                "structured_logging": settings.logging.structured_logging
            },
            "jwt_config": {
                "algorithm": settings.jwt.algorithm,
                "access_token_expire_minutes": settings.jwt.access_token_expire_minutes,
                "refresh_token_expire_days": settings.jwt.refresh_token_expire_days
            }
        }
    
    print("✅ 应用创建完成")
    print()
    
    # 6. 初始化数据库
    print("🗄️ 初始化数据库...")
    try:
        import asyncio
        asyncio.run(init_database())
        print("✅ 数据库初始化完成")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
    
    print()
    print("🎉 .env 配置演示完成！")
    print("=" * 60)
    print("🌐 访问地址:")
    print("   📚 API文档: http://localhost:8000/docs")
    print("   🏠 首页: http://localhost:8000/")
    print("   ⚙️ 配置信息: http://localhost:8000/config")
    print()
    print("💡 配置说明:")
    print("   • 所有配置都从 .env 文件自动加载")
    print("   • 使用 PYADVINCEKIT_ 前缀避免冲突")
    print("   • 支持环境变量覆盖 .env 文件配置")
    print("   • 配置变更后调用 reload_settings() 重新加载")
    print()
    
    return app


def demo_custom_config():
    """演示自定义配置的使用"""
    print("=== 自定义配置演示 ===")
    print()
    
    # 1. 创建自定义配置
    custom_settings = Settings(
        app_name="自定义应用",
        debug=True,
        environment="development",
        database={
            "database_url": "sqlite:///./custom_app.db",
            "pool_size": 5
        },
        logging={
            "log_level": "DEBUG",
            "log_file_path": "logs/custom_app.log"
        }
    )
    
    print("📋 自定义配置:")
    print(f"   应用名称: {custom_settings.app_name}")
    print(f"   数据库URL: {custom_settings.database.database_url}")
    print(f"   日志级别: {custom_settings.logging.log_level}")
    print()
    
    # 2. 使用自定义配置创建应用
    from pyadvincekit.core.app_factory import FastAPIAppFactory
    
    app_factory = FastAPIAppFactory(settings=custom_settings)
    app = app_factory.create_app(
        title=custom_settings.app_name,
        description="使用自定义配置的应用",
        version="1.0.0"
    )
    
    print("✅ 自定义配置应用创建完成")
    print()
    
    return app


def demo_config_override():
    """演示配置覆盖机制"""
    print("=== 配置覆盖演示 ===")
    print()
    
    # 1. 环境变量覆盖 .env 文件
    import os
    
    # 设置环境变量（会覆盖 .env 文件中的配置）
    os.environ["PYADVINCEKIT_APP_NAME"] = "环境变量覆盖的应用"
    os.environ["PYADVINCEKIT_DEBUG"] = "false"
    os.environ["PYADVINCEKIT_LOG_LEVEL"] = "WARNING"
    
    print("🔧 设置环境变量覆盖:")
    print("   PYADVINCEKIT_APP_NAME=环境变量覆盖的应用")
    print("   PYADVINCEKIT_DEBUG=false")
    print("   PYADVINCEKIT_LOG_LEVEL=WARNING")
    print()
    
    # 2. 重新加载配置
    settings = reload_settings()
    
    print("📋 覆盖后的配置:")
    print(f"   应用名称: {settings.app_name}")
    print(f"   调试模式: {settings.debug}")
    print(f"   日志级别: {settings.logging.log_level}")
    print()
    
    # 3. 清理环境变量
    for key in ["PYADVINCEKIT_APP_NAME", "PYADVINCEKIT_DEBUG", "PYADVINCEKIT_LOG_LEVEL"]:
        if key in os.environ:
            del os.environ[key]
    
    print("🧹 已清理环境变量")
    print()


def main():
    """主函数"""
    print("🚀 PyAdvanceKit .env 配置演示")
    print("=" * 60)
    print()
    
    # 演示 .env 配置
    app1 = demo_env_config()
    
    print("\n" + "=" * 60 + "\n")
    
    # 演示自定义配置
    app2 = demo_custom_config()
    
    print("\n" + "=" * 60 + "\n")
    
    # 演示配置覆盖
    demo_config_override()
    
    print("🎯 总结:")
    print("   1. .env 文件配置 - 最简单的方式")
    print("   2. 自定义配置 - 程序化配置")
    print("   3. 环境变量覆盖 - 部署时配置")
    print("   4. 配置重载 - 动态更新配置")
    print()
    
    # 启动应用（可选）
    import uvicorn
    
    print("🌐 启动应用...")
    print("   按 Ctrl+C 停止应用")
    print()
    
    uvicorn.run(
        app1,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()

