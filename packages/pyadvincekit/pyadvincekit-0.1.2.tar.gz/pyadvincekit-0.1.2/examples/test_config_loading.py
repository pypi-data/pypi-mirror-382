"""
测试配置加载机制
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_config_loading():
    """测试配置加载"""
    print("=== 测试配置加载 ===")
    
    # 1. 检查 .env 文件
    env_file = Path(__file__).parent / "test_env.env"
    print(f"检查 .env 文件: {env_file}")
    print(f"文件存在: {env_file.exists()}")
    
    if env_file.exists():
        print("文件内容:")
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
        print()
    
    # 2. 导入配置
    print("导入配置...")
    from pyadvincekit.core.config import Settings, get_settings
    
    # 3. 创建配置实例
    print("创建配置实例...")
    settings = Settings()
    
    print("配置信息:")
    print(f"  应用名称: {settings.app_name}")
    print(f"  调试模式: {settings.debug}")
    print(f"  环境: {settings.environment}")
    print(f"  数据库URL: {settings.database.url}")
    print(f"  数据库连接池大小: {settings.database.pool_size}")
    print(f"  日志级别: {settings.logging.level}")
    print(f"  日志文件: {settings.logging.log_file_path}")
    print(f"  JWT密钥长度: {len(settings.security.secret_key)}")
    print()
    
    # 4. 测试 get_settings()
    print("测试 get_settings():")
    settings2 = get_settings()
    print(f"  数据库URL: {settings2.database.url}")
    print(f"  日志级别: {settings2.logging.level}")
    print()
    
    # 5. 检查环境变量
    import os
    print("环境变量:")
    for key, value in os.environ.items():
        if key.startswith("PYADVINCEKIT_"):
            print(f"  {key} = {value}")

if __name__ == "__main__":
    test_config_loading()

