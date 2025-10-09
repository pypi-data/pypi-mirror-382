"""
    结构化日志 ， 配置管理

"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入PyAdvanceKit功能
from pyadvincekit.logging import setup_logging, get_logger
from pyadvincekit.core.config import get_settings
from pyadvincekit.auth import (
    JWTAuth, create_access_token, verify_token,
    Permission, require_permission, check_permission
)
from pyadvincekit.utils import (
    # 安全工具
    generate_secret_key, hash_password, verify_password,
    encrypt_data, decrypt_data, md5_hash,
    # 日期时间工具
    now, utc_now, format_duration, humanize_datetime,
    timestamp_to_datetime, datetime_to_timestamp,
    # 数据验证工具
    validate_email, validate_phone, validate_password_strength,
    create_validator, DataValidator
)
from pyadvincekit.core.config import Settings

async def demo_logging_system():
    """演示结构化日志系统"""
    print("=== 结构化日志系统演示 ===")

    # 设置日志系统
    settings = Settings(
        logging={
            "log_level": "INFO",
            "structured_logging": True,
            "log_file_enabled": False  # 演示时不写文件
        }
    )
    setup_logging(settings)

    # 获取日志器
    logger = get_logger("demo.logging")

    # 基础日志
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")

    # 带上下文的结构化日志
    logger.info("用户登录", extra={
        "user_id": "12345",
        "ip_address": "192.168.1.100",
        "action": "login"
    })

    # 性能日志
    start_time = datetime.now()
    await asyncio.sleep(0.1)  # 模拟操作
    duration = (datetime.now() - start_time).total_seconds()

    logger.info("操作完成", extra={
        "operation": "data_processing",
        "duration": duration,
        "records_processed": 1000
    })

    print("✅ 日志系统演示完成")
    print()


def example_basic_config():
    """基础配置示例"""
    print("=== 基础配置示例 ===")

    # 创建默认配置
    settings = Settings()

    print(f"应用名称: {settings.app_name}")
    print(f"运行环境: {settings.environment}")
    print(f"调试模式: {settings.debug}")
    print(f"服务器地址: {settings.host}:{settings.port}")
    print(f"数据库URL: {settings.database_url}")
    print(f"日志级别: {settings.log_level}")
    print()


def example_environment_config():
    """环境配置示例"""
    print("=== 环境配置示例 ===")

    # 开发环境
    dev_settings = Settings(environment="development")
    print(f"开发环境 - Debug: {dev_settings.debug}")
    print(f"开发环境 - 文档URL: {dev_settings.docs_url}")

    # 测试环境
    test_settings = Settings(environment="testing")
    print(f"测试环境 - Debug: {test_settings.debug}")
    print(f"测试环境 - 文档URL: {test_settings.docs_url}")

    # 生产环境
    prod_settings = Settings(environment="production")
    print(f"生产环境 - Debug: {prod_settings.debug}")
    print(f"生产环境 - 文档URL: {prod_settings.docs_url}")
    print()


def example_custom_config():
    """自定义配置示例"""
    print("=== 自定义配置示例 ===")

    # 自定义配置参数
    custom_settings = Settings(
        app_name="我的应用",
        environment="development",
        port=8080,
        database={
            "database_url": "postgresql://user:pass@localhost/mydb",
            "pool_size": 20,
            "echo_sql": True
        },
        logging={
            "log_level": "DEBUG",
            "log_file_enabled": True,
            "log_file_path": "logs/my_app.log"
        }
    )

    print(f"应用名称: {custom_settings.app_name}")
    print(f"服务器端口: {custom_settings.port}")
    print(f"数据库URL: {custom_settings.database_url}")
    print(f"连接池大小: {custom_settings.database_pool_size}")
    print(f"SQL日志: {custom_settings.database_echo_sql}")
    print(f"日志级别: {custom_settings.log_level}")
    print(f"日志文件: {custom_settings.log_file_path}")
    print()

def example_database_url_conversion():
    """数据库URL转换示例"""
    print("=== 数据库URL转换示例 ===")

    settings = Settings()

    # 设置不同类型的数据库URL
    database_urls = [
        "postgresql://user:pass@localhost/db",
        "mysql://user:pass@localhost/db",
        "sqlite:///./test.db"
    ]

    for url in database_urls:
        settings.database_url = url

        sync_url = settings.get_database_url(async_driver=False)
        async_url = settings.get_database_url(async_driver=True)

        print(f"原始URL: {url}")
        print(f"同步URL: {sync_url}")
        print(f"异步URL: {async_url}")
        print("-" * 50)
    print()

def example_config_validation():
    """配置验证示例"""
    print("=== 配置验证示例 ===")

    try:
        # 有效配置
        valid_settings = Settings(port=8080)
        print(f"有效端口: {valid_settings.port}")

        # 无效配置（会抛出验证错误）
        try:
            invalid_settings = Settings(port=0)
        except Exception as e:
            print(f"无效端口错误: {e}")

        try:
            invalid_settings = Settings(port=70000)
        except Exception as e:
            print(f"端口超出范围错误: {e}")

    except Exception as e:
        print(f"配置验证错误: {e}")
    print()


def example_config_file():
    """配置文件示例"""
    print("=== 配置文件示例 ===")
    from dotenv import load_dotenv
    load_dotenv(".env")
    settings = get_settings()

    print(f"应用名称: {settings.app_name}")
    print(f"服务器端口: {settings.port}")
    print(f"数据库URL: {settings.database_url}")
    print(f"连接池大小: {settings.database_pool_size}")
    print(f"SQL日志: {settings.database_echo_sql}")
    print(f"日志级别: {settings.log_level}")
    print(f"日志文件: {settings.log_file_path}")


if __name__ == "__main__":
    print("🚀 PyAdvanceKit 配置管理示例")
    print("=" * 50)

    # 运行所有示例
    example_basic_config()
    example_environment_config()
    example_custom_config()
    example_database_url_conversion()
    example_config_validation()
    example_config_file()

    print("✅ 配置管理示例完成！")
    print("\n💡 提示:")
    print("1. 在生产环境中，请使用环境变量或 .env 文件设置敏感配置")
    print("2. 不同环境可以使用不同的配置文件")
    print("3. 所有配置都有类型验证，确保配置的正确性")

