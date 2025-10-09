"""
PyAdvanceKit 自动配置加载演示

演示外部项目创建 .env 文件后，pyadvincekit 如何自动加载和应用配置
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径（仅用于演示）
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def demo_auto_config_loading():
    """演示自动配置加载机制"""
    print("=== PyAdvanceKit 自动配置加载演示 ===")
    print()
    
    # 1. 检查 .env 文件
    env_file = Path(__file__).parent / "test_env.env"
    if env_file.exists():
        print(f"✅ 发现 .env 文件: {env_file}")
        print("📄 .env 文件内容:")
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # print("   " + "\n   ".join(content.strip().split('\n')))
        print()
    else:
        print(f"⚠️ 未发现 .env 文件: {env_file}")
        print("   请创建 .env 文件来演示自动配置加载")
        print()
        return
    
    # 2. 导入 pyadvincekit（这里会触发自动配置加载）
    print("🔄 导入 pyadvincekit...")
    print("   此时 pyadvincekit 内部会自动执行：")
    print("   1. 查找当前目录的 .env 文件")
    print("   2. 解析 PYADVINCEKIT_* 变量")
    print("   3. 映射到配置字段")
    print("   4. 创建配置对象")
    print()
    
    # 导入 pyadvincekit（触发自动配置加载）
    from pyadvincekit import create_app
    from pyadvincekit.core.config import get_settings
    
    print("✅ pyadvincekit 导入完成，配置已自动加载")
    print()
    
    # 3. 获取已加载的配置
    print("📋 获取自动加载的配置:")
    settings = get_settings()
    
    print(f"   应用名称: {settings.app_name}")
    print(f"   应用版本: {settings.app_version}")
    print(f"   调试模式: {settings.debug}")
    print(f"   环境: {settings.environment}")
    print(f"   数据库URL: {settings.database_url}")
    print(f"   日志级别: {settings.log_level}")
    print(f"   日志文件: {settings.log_file_path}")
    print(f"   JWT过期时间: {settings.jwt_access_token_expire_minutes}分钟")
    print()
    
    # 4. 创建应用（使用已加载的配置）
    print("🚀 创建 FastAPI 应用...")
    app = create_app(
        title=settings.app_name,
        description="使用自动加载配置的应用",
        version="1.0.0"
    )
    
    # 5. 添加配置展示路由
    @app.get("/")
    async def root():
        """根路径 - 展示自动加载的配置"""
        return {
            "message": "PyAdvanceKit 自动配置加载演示",
            "config_source": ".env 文件自动加载",
            "config": {
                "app_name": settings.app_name,
                "debug": settings.debug,
                "environment": settings.environment,
                "database_url": settings.database_url,
                "log_level": settings.log_level,
                "log_file": settings.log_file_path
            },
            "note": "所有配置都来自 .env 文件的自动加载"
        }
    
    @app.get("/config-details")
    async def config_details():
        """详细的配置信息"""
        return {
            "config_loading_mechanism": {
                "trigger": "模块导入时自动触发",
                "file_discovery": "自动查找当前目录的 .env 文件",
                "variable_parsing": "自动解析 PYADVINCEKIT_* 变量",
                "field_mapping": "自动映射到配置字段",
                "type_conversion": "自动类型转换和验证"
            },
            "current_config": {
                "app_config": {
                    "app_name": settings.app_name,
                    "debug": settings.debug,
                    "environment": settings.environment
                },
                "database_config": {
                    "database_url": settings.database_url,
                    "pool_size": settings.database_pool_size,
                    "max_overflow": settings.database_max_overflow
                },
                "logging_config": {
                    "log_level": settings.log_level,
                    "log_file_enabled": settings.log_file_enabled,
                    "log_file_path": settings.log_file_path,
                    "structured_logging": settings.log_structured_logging
                },
                "jwt_config": {
                    "secret_key": settings.jwt_secret_key[:20] + "...",
                    "access_token_expire_minutes": settings.jwt_access_token_expire_minutes,
                    "refresh_token_expire_days": settings.jwt_refresh_token_expire_days
                }
            },
            "env_file_path": str(env_file),
            "loading_time": "模块导入时自动加载"
        }
    
    print("✅ 应用创建完成")
    print()
    
    # 6. 展示配置加载的完整流程
    print("🔍 配置加载流程详解:")
    print("   1. 外部项目创建 .env 文件")
    print("   2. 外部项目导入 pyadvincekit")
    print("   3. pyadvincekit 内部自动执行 Settings()")
    print("   4. Settings() 自动查找 .env 文件")
    print("   5. 解析 PYADVINCEKIT_* 变量")
    print("   6. 映射到配置字段")
    print("   7. 创建配置对象")
    print("   8. 配置立即生效")
    print()
    
    print("🎉 自动配置加载演示完成！")
    print("=" * 60)
    print("🌐 访问地址:")
    print("   📚 API文档: http://localhost:8000/docs")
    print("   🏠 首页: http://localhost:8000/")
    print("   ⚙️ 配置详情: http://localhost:8000/config-details")
    print()
    print("💡 关键特点:")
    print("   • 零配置使用 - 只需创建 .env 文件")
    print("   • 自动发现 - 自动查找 .env 文件")
    print("   • 智能映射 - 自动映射变量到配置字段")
    print("   • 类型安全 - 自动类型转换和验证")
    print("   • 立即生效 - 配置加载后立即生效")
    print()
    
    return app


def demo_config_override():
    """演示配置覆盖机制"""
    print("=== 配置覆盖机制演示 ===")
    print()
    
    # 1. 设置环境变量（会覆盖 .env 文件）
    import os
    
    print("🔧 设置环境变量覆盖 .env 文件:")
    os.environ["PYADVINCEKIT_APP_NAME"] = "环境变量覆盖的应用"
    os.environ["PYADVINCEKIT_DEBUG"] = "false"
    os.environ["PYADVINCEKIT_LOG_LEVEL"] = "WARNING"
    
    print("   PYADVINCEKIT_APP_NAME=环境变量覆盖的应用")
    print("   PYADVINCEKIT_DEBUG=false")
    print("   PYADVINCEKIT_LOG_LEVEL=WARNING")
    print()
    
    # 2. 重新加载配置
    from pyadvincekit.core.config import reload_settings
    
    print("🔄 重新加载配置...")
    settings = reload_settings()
    
    print("📋 覆盖后的配置:")
    print(f"   应用名称: {settings.app_name}")
    print(f"   调试模式: {settings.debug}")
    print(f"   日志级别: {settings.log_level}")
    print()
    
    # 3. 清理环境变量
    for key in ["PYADVINCEKIT_APP_NAME", "PYADVINCEKIT_DEBUG", "PYADVINCEKIT_LOG_LEVEL"]:
        if key in os.environ:
            del os.environ[key]
    
    print("🧹 已清理环境变量")
    print()


def main():
    """主函数"""
    print("🚀 PyAdvanceKit 自动配置加载演示")
    print("=" * 60)
    print()
    
    # 演示自动配置加载
    app = demo_auto_config_loading()
    
    if app:
        print("\n" + "=" * 60 + "\n")
        
        # 演示配置覆盖
        demo_config_override()
        
        print("\n" + "=" * 60 + "\n")
        
        print("🎯 总结:")
        print("   PyAdvanceKit 的自动配置加载机制使得外部项目可以：")
        print("   1. 只需创建 .env 文件")
        print("   2. 导入 pyadvincekit 时自动加载配置")
        print("   3. 无需任何额外的配置加载代码")
        print("   4. 支持环境变量覆盖")
        print("   5. 提供类型安全的配置管理")
        print()
        
        # 启动应用
        import uvicorn
        
        print("🌐 启动应用...")
        print("   按 Ctrl+C 停止应用")
        print()
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )


if __name__ == "__main__":
    main()
