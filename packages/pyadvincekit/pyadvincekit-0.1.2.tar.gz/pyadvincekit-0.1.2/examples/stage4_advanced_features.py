"""
阶段四：功能完善层示例

演示 PyAdvanceKit 的高级功能：
- 结构化日志系统
- JWT认证和权限系统
- 安全工具函数
- 数据验证工具
- 日期时间工具
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


def demo_jwt_auth():
    """演示JWT认证系统"""
    print("=== JWT认证系统演示 ===")
    
    # 创建JWT认证实例
    jwt_auth = JWTAuth()
    
    # 1. 创建访问令牌
    user_id = "user123"
    access_token = jwt_auth.create_access_token(
        subject=user_id,
        extra_claims={"role": "admin", "permissions": ["read", "write"]}
    )
    print(f"✅ 访问令牌创建成功: {access_token[:50]}...")
    
    # 2. 验证令牌
    try:
        payload = jwt_auth.verify_token(access_token)
        print(f"✅ 令牌验证成功，用户ID: {payload['sub']}, 角色: {payload.get('role')}")
    except Exception as e:
        print(f"❌ 令牌验证失败: {e}")
    
    # 3. 创建刷新令牌
    refresh_token = jwt_auth.create_refresh_token(user_id)
    print(f"✅ 刷新令牌创建成功: {refresh_token[:50]}...")
    
    # 4. 使用刷新令牌生成新的访问令牌
    try:
        new_access_token = jwt_auth.refresh_access_token(refresh_token)
        print(f"✅ 新访问令牌生成成功: {new_access_token[:50]}...")
    except Exception as e:
        print(f"❌ 刷新令牌失败: {e}")
    
    # 5. 密码哈希和验证
    password = "MySecurePassword123!"
    hashed_password = jwt_auth.hash_password(password)
    print(f"✅ 密码哈希成功: {hashed_password[:50]}...")
    
    is_valid = jwt_auth.verify_password(password, hashed_password)
    print(f"✅ 密码验证结果: {is_valid}")
    
    print()


def demo_permission_system():
    """演示权限系统"""
    print("=== 权限系统演示 ===")
    
    # 检查用户权限
    user_id = "admin_user"
    
    # 模拟用户角色提供者
    def get_user_roles(user_id: str):
        role_mapping = {
            "admin_user": ["admin"],
            "normal_user": ["user"],
            "super_admin": ["super_admin"]
        }
        return role_mapping.get(user_id, ["guest"])
    
    # 设置角色提供者（在实际应用中应该从数据库获取）
    from pyadvincekit.auth.permissions import set_user_role_provider
    set_user_role_provider(get_user_roles)
    
    # 测试权限检查
    permissions_to_test = [
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.ADMIN_READ,
        Permission.SYSTEM_CONFIG
    ]
    
    for permission in permissions_to_test:
        has_permission = check_permission(user_id, permission)
        status = "✅ 有权限" if has_permission else "❌ 无权限"
        print(f"{status}: {user_id} - {permission.value}")
    
    print()


def demo_security_utils():
    """演示安全工具"""
    print("=== 安全工具演示 ===")
    
    # 1. 生成安全密钥
    secret_key = generate_secret_key(32)
    print(f"✅ 生成密钥: {secret_key}")
    
    # 2. 密码哈希
    password = "MyPassword123"
    hashed_password, salt = hash_password(password)
    print(f"✅ 密码哈希: {hashed_password[:30]}...")
    print(f"✅ 盐值: {salt[:30]}...")
    
    # 验证密码
    is_valid = verify_password(password, hashed_password, salt)
    print(f"✅ 密码验证结果: {is_valid}")
    
    # 3. 数据加密
    sensitive_data = "这是需要加密的敏感数据"
    encryption_password = "encryption_key_123"
    
    encrypted_data = encrypt_data(sensitive_data, encryption_password)
    print(f"✅ 数据加密: {encrypted_data[:50]}...")
    
    decrypted_data = decrypt_data(encrypted_data, encryption_password)
    print(f"✅ 数据解密: {decrypted_data}")
    
    # 4. 哈希计算
    data = "Hello, World!"
    md5_result = md5_hash(data)
    print(f"✅ MD5哈希: {md5_result}")
    
    print()


def demo_datetime_utils():
    """演示日期时间工具"""
    print("=== 日期时间工具演示 ===")
    
    # 1. 获取当前时间
    current_time = utc_now()
    beijing_time = now(tz=None)  # 使用默认时区
    print(f"✅ 当前UTC时间: {current_time}")
    print(f"✅ 当前本地时间: {beijing_time}")
    
    # 2. 时间戳转换
    timestamp = datetime_to_timestamp(current_time)
    converted_time = timestamp_to_datetime(timestamp)
    print(f"✅ 时间戳: {timestamp}")
    print(f"✅ 转换回的时间: {converted_time}")
    
    # 3. 持续时间格式化
    durations = [30, 90, 3600, 86400, 90000]
    for duration in durations:
        formatted = format_duration(duration)
        print(f"✅ {duration}秒 = {formatted}")
    
    # 4. 人性化时间显示
    past_times = [
        current_time - timedelta(minutes=5),
        current_time - timedelta(hours=2),
        current_time - timedelta(days=1),
        current_time - timedelta(days=30),
    ]
    
    for past_time in past_times:
        humanized = humanize_datetime(past_time, current_time)
        print(f"✅ 人性化时间: {humanized}")
    
    print()


def demo_data_validation():
    """演示数据验证工具"""
    print("=== 数据验证工具演示 ===")
    
    # 1. 单个验证函数
    test_data = [
        ("邮箱验证", "user@example.com", validate_email),
        ("邮箱验证", "invalid-email", validate_email),
        ("手机号验证", "13812345678", validate_phone),
        ("手机号验证", "123456", validate_phone),
        ("密码强度", "StrongPass123!", validate_password_strength),
        ("密码强度", "weak", validate_password_strength),
    ]
    
    for test_name, value, validator in test_data:
        result = validator(value)
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {test_name} - {value}")
    
    # 2. 数据验证器链式调用
    print("\n--- 链式验证演示 ---")
    
    # 用户注册数据验证
    user_data = {
        "username": "john_doe",
        "email": "john@example.com",
        "phone": "13812345678",
        "password": "SecurePass123!",
        "age": 25
    }
    
    validator = create_validator()
    
    # 链式验证
    validator.validate_required(user_data.get("username"), "用户名") \
        .validate_length(user_data.get("username"), 3, 20, "用户名") \
        .validate_email(user_data.get("email"), "邮箱") \
        .validate_phone(user_data.get("phone"), "手机号") \
        .validate_password_strength(user_data.get("password"), "密码") \
        .validate_range(user_data.get("age"), 18, 100, "年龄")
    
    if validator.is_valid():
        print("✅ 用户数据验证通过")
    else:
        print("❌ 用户数据验证失败:")
        for error in validator.get_errors():
            print(f"   - {error}")
    
    # 3. 无效数据验证
    invalid_data = {
        "username": "",  # 空用户名
        "email": "invalid-email",  # 无效邮箱
        "phone": "123",  # 无效手机号
        "password": "weak",  # 弱密码
        "age": 10  # 年龄不符
    }
    
    invalid_validator = create_validator()
    invalid_validator.validate_required(invalid_data.get("username"), "用户名") \
        .validate_email(invalid_data.get("email"), "邮箱") \
        .validate_phone(invalid_data.get("phone"), "手机号") \
        .validate_password_strength(invalid_data.get("password"), "密码") \
        .validate_range(invalid_data.get("age"), 18, 100, "年龄")
    
    print("\n--- 无效数据验证演示 ---")
    if not invalid_validator.is_valid():
        print("❌ 验证失败（预期结果）:")
        for error in invalid_validator.get_errors():
            print(f"   - {error}")
    
    print()


async def main():
    """主函数"""
    print("🚀 PyAdvanceKit 阶段四：功能完善层演示")
    print("=" * 60)
    
    try:
        # 演示所有高级功能
        await demo_logging_system()
        demo_jwt_auth()
        demo_permission_system()
        demo_security_utils()
        demo_datetime_utils()
        demo_data_validation()
        
        print("✅ 阶段四功能演示完成！")
        print("\n💡 阶段四新增功能总结:")
        print("1. 🔒 结构化日志系统 - 支持JSON格式、彩色输出、请求追踪")
        print("2. 🔑 JWT认证系统 - 令牌生成、验证、刷新功能")
        print("3. 🛡️ 权限系统 - 基于角色的访问控制(RBAC)")
        print("4. 🔐 安全工具库 - 加密、哈希、密钥生成")
        print("5. ⏰ 日期时间工具 - 时区处理、格式化、人性化显示")
        print("6. ✅ 数据验证工具 - 邮箱、手机号、密码强度等验证")
        print("\n🎯 这些功能让 PyAdvanceKit 成为功能完整的企业级框架！")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
