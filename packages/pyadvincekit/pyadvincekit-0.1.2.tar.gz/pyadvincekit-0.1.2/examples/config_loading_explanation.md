# PyAdvanceKit 配置加载机制详解

## 1. 配置加载的核心机制

### 1.1 Pydantic Settings 基础

PyAdvanceKit 使用 **Pydantic Settings** 来管理配置，这是基于 Pydantic V2 的配置管理系统。

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",           # 指定 .env 文件路径
        env_file_encoding="utf-8", # 文件编码
        env_prefix="PYADVINCEKIT_", # 环境变量前缀
        case_sensitive=False,      # 不区分大小写
        extra="forbid"            # 禁止额外字段
    )
```

### 1.2 配置加载顺序

Pydantic Settings 按以下优先级加载配置：

1. **环境变量** (最高优先级)
2. **`.env` 文件**
3. **默认值** (最低优先级)

## 2. 配置加载流程详解

### 2.1 自动加载机制

当创建 `Settings()` 实例时，Pydantic 会自动：

```python
# 在 pyadvincekit/core/config.py 第353行
settings = Settings()  # 这里会自动加载配置
```

**自动加载过程**：
1. 查找当前工作目录的 `.env` 文件
2. 读取文件内容并解析
3. 将变量名转换为配置字段名
4. 应用环境变量覆盖
5. 验证配置类型和值

### 2.2 环境变量映射

`.env` 文件中的变量名会被映射到配置字段：

```bash
# .env 文件
PYADVINCEKIT_APP_NAME=我的应用
PYADVINCEKIT_DEBUG=true
PYADVINCEKIT_DATABASE_URL=sqlite:///./app.db
```

映射到配置字段：
```python
class Settings(BaseSettings):
    app_name: str = "PyAdvanceKit App"      # ← PYADVINCEKIT_APP_NAME
    debug: bool = False                     # ← PYADVINCEKIT_DEBUG
    database: DatabaseConfig                # ← PYADVINCEKIT_DATABASE_URL
```

### 2.3 嵌套配置处理

对于嵌套配置，使用下划线分隔：

```bash
# .env 文件
PYADVINCEKIT_DATABASE_URL=sqlite:///./app.db
PYADVINCEKIT_DATABASE_POOL_SIZE=10
PYADVINCEKIT_LOG_LEVEL=INFO
PYADVINCEKIT_LOG_FILE_PATH=logs/app.log
```

映射到嵌套配置：
```python
class DatabaseConfig(BaseSettings):
    database_url: str = "sqlite:///./app.db"  # ← PYADVINCEKIT_DATABASE_URL
    pool_size: int = 10                       # ← PYADVINCEKIT_DATABASE_POOL_SIZE

class LoggingConfig(BaseSettings):
    log_level: str = "INFO"                   # ← PYADVINCEKIT_LOG_LEVEL
    log_file_path: str = "logs/app.log"       # ← PYADVINCEKIT_LOG_FILE_PATH

class Settings(BaseSettings):
    database: DatabaseConfig
    logging: LoggingConfig
```

## 3. 配置加载的具体实现

### 3.1 全局配置实例

```python
# pyadvincekit/core/config.py 第352-356行
# 全局配置实例
settings = Settings()

# 确保日志目录存在
settings.create_log_directory()
```

**关键点**：
- 在模块导入时创建全局配置实例
- 自动加载 `.env` 文件（如果存在）
- 立即创建必要的目录

### 3.2 配置重载机制

```python
# pyadvincekit/core/config.py 第364-369行
def reload_settings() -> Settings:
    """重新加载配置"""
    global settings
    settings = Settings()  # 重新创建实例，重新加载配置
    settings.create_log_directory()
    return settings
```

**使用场景**：
- 修改 `.env` 文件后需要重新加载
- 程序运行时动态更新配置
- 测试时重置配置

### 3.3 配置获取

```python
# pyadvincekit/core/config.py 第359-361行
def get_settings() -> Settings:
    """获取配置实例"""
    return settings
```

## 4. 配置管理器的增强功能

### 4.1 自动 .env 文件发现

```python
# pyadvincekit/core/config_manager.py 第30-55行
def _find_env_file(self, env_file_path: Optional[Union[str, Path]]) -> Optional[Path]:
    """查找 .env 文件"""
    if env_file_path:
        path = Path(env_file_path)
        if path.exists():
            return path
        else:
            logger.warning(f"指定的 .env 文件不存在: {path}")
            return None
    
    # 自动查找 .env 文件
    current_dir = Path.cwd()
    possible_paths = [
        current_dir / ".env",
        current_dir / ".env.local",
        current_dir / ".env.development",
        current_dir / ".env.production",
    ]
    
    for path in possible_paths:
        if path.exists():
            logger.info(f"发现 .env 文件: {path}")
            return path
    
    logger.info("未发现 .env 文件，将使用默认配置")
    return None
```

### 4.2 手动 .env 文件加载

```python
# pyadvincekit/core/config_manager.py 第57-81行
def load_env_file(self) -> bool:
    """加载 .env 文件"""
    if not self.env_file_path:
        return False
    
    try:
        from dotenv import load_dotenv
        load_dotenv(self.env_file_path, encoding='utf-8')
        logger.info(f"成功加载 .env 文件: {self.env_file_path}")
        return True
    except ImportError:
        logger.warning("未安装 python-dotenv，无法加载 .env 文件")
        logger.info("安装命令: pip install python-dotenv")
        return False
    except Exception as e:
        logger.error(f"加载 .env 文件失败: {e}")
        return False
```

## 5. 配置加载的完整流程

### 5.1 应用启动时的配置加载

```python
# 1. 导入 pyadvincekit
from pyadvincekit import create_app

# 2. 此时会自动执行：
#    - 创建 Settings() 实例
#    - 自动查找并加载 .env 文件
#    - 应用环境变量覆盖
#    - 验证配置

# 3. 创建应用
app = create_app()
```

### 5.2 手动配置加载

```python
from pyadvincekit import setup_from_env_file

# 手动指定 .env 文件路径
settings = setup_from_env_file(".env")
```

### 5.3 配置覆盖

```python
import os
from pyadvincekit import reload_settings

# 设置环境变量（会覆盖 .env 文件）
os.environ["PYADVINCEKIT_APP_NAME"] = "覆盖的应用名"
os.environ["PYADVINCEKIT_DEBUG"] = "false"

# 重新加载配置
settings = reload_settings()
```

## 6. 配置验证和类型转换

### 6.1 自动类型转换

```python
# .env 文件中的字符串会自动转换为对应类型
PYADVINCEKIT_DEBUG=true          # → bool: True
PYADVINCEKIT_PORT=8000           # → int: 8000
PYADVINCEKIT_POOL_SIZE=10        # → int: 10
PYADVINCEKIT_LOG_LEVEL=INFO      # → str: "INFO"
```

### 6.2 配置验证

```python
class Settings(BaseSettings):
    port: int = Field(default=8000, ge=1, le=65535)  # 端口范围验证
    debug: bool = Field(default=False)               # 布尔值验证
    environment: Environment = Field(default=Environment.DEVELOPMENT)  # 枚举验证
```

### 6.3 验证器

```python
@validator("debug")
def validate_debug_by_env(cls, v: bool, values: Dict[str, Any]) -> bool:
    """根据环境自动设置debug模式"""
    env = values.get("environment")
    if env == Environment.PRODUCTION:
        return False  # 生产环境强制关闭debug
    return v
```

## 7. 实际使用示例

### 7.1 基本使用

```python
# 1. 创建 .env 文件
# PYADVINCEKIT_APP_NAME=我的应用
# PYADVINCEKIT_DEBUG=true
# PYADVINCEKIT_DATABASE_URL=sqlite:///./app.db

# 2. 在代码中使用
from pyadvincekit import get_settings

settings = get_settings()
print(settings.app_name)        # 输出: 我的应用
print(settings.debug)           # 输出: True
print(settings.database.database_url)  # 输出: sqlite:///./app.db
```

### 7.2 配置管理器使用

```python
from pyadvincekit import ConfigManager

# 创建配置管理器
config_manager = ConfigManager(".env")

# 加载配置
settings = config_manager.setup_pyadvincekit()

# 创建应用
app = config_manager.create_app_with_config(app_title="我的应用")
```

## 8. 总结

PyAdvanceKit 的配置加载机制具有以下特点：

1. **自动化**：导入时自动加载配置，无需手动调用
2. **灵活性**：支持多种配置来源和覆盖机制
3. **类型安全**：基于 Pydantic 的类型验证和转换
4. **环境感知**：根据环境自动调整配置
5. **易于使用**：提供多种便捷的配置管理方式

这种设计使得外部项目可以非常方便地通过 `.env` 文件配置 PyAdvanceKit，同时保持了配置的灵活性和可维护性。

