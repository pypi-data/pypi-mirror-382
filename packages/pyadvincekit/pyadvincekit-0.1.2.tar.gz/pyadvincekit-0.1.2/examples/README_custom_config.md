# 自定义配置数据库连接

## 📋 概述

PyAdvanceKit 提供了多种方式来配置数据库连接，让外部调用方可以灵活地设置自己的配置，而不需要修改内部包的代码。

## 🎯 核心思想

- **外部调用方**（如 `examples`）负责配置
- **内部包**（`pyadvincekit`）提供配置接口
- **配置传递**：通过 `Settings()` 构造函数和 `DatabaseManager(settings)` 实现

## 🚀 配置方式

### 方式1: 使用 .env 文件

```python
from dotenv import load_dotenv
from pyadvincekit.core.config import Settings
from pyadvincekit.core.database import DatabaseManager

# 1. 加载 .env 文件
load_dotenv("path/to/.env")

# 2. 创建配置（自动读取环境变量）
settings = Settings()

# 3. 创建数据库管理器
db_manager = DatabaseManager(settings)
```

### 方式2: 直接使用 Settings() 构造函数

```python
from pyadvincekit.core.config import Settings
from pyadvincekit.core.database import DatabaseManager

# 1. 直接设置配置
settings = Settings(
    database={
        "database_url": "sqlite:///./my_app.db",
        "echo_sql": True,
        "pool_size": 5
    },
    environment="development",
    debug=True
)

# 2. 创建数据库管理器
db_manager = DatabaseManager(settings)
```

### 方式3: 混合方式（推荐）

```python
from dotenv import load_dotenv
from pyadvincekit.core.config import Settings
from pyadvincekit.core.database import DatabaseManager

# 1. 加载 .env 文件（基础配置）
load_dotenv("path/to/.env")

# 2. 创建基础配置
base_settings = Settings()

# 3. 覆盖特定配置
custom_settings = Settings(
    database={
        "database_url": "sqlite:///./my_custom_app.db",  # 覆盖 .env 中的设置
        "echo_sql": True
    }
)

# 4. 创建数据库管理器
db_manager = DatabaseManager(custom_settings)
```

## 📝 .env 文件示例

```bash
# 数据库配置
PYADVINCEKIT_DATABASE_URL=sqlite:///./my_app.db
PYADVINCEKIT_DATABASE_ECHO_SQL=true
PYADVINCEKIT_DATABASE_POOL_SIZE=5

# 应用配置
PYADVINCEKIT_ENVIRONMENT=development
PYADVINCEKIT_DEBUG=true
```

## 🔧 完整示例

```python
import asyncio
from pyadvincekit.core.config import Settings
from pyadvincekit.core.database import DatabaseManager
from pyadvincekit import BaseModel, BaseCRUD

# 1. 配置数据库连接
settings = Settings(
    database={
        "database_url": "sqlite:///./my_app.db",
        "echo_sql": True
    }
)

# 2. 创建数据库管理器
db_manager = DatabaseManager(settings)

# 3. 定义模型
class User(BaseModel):
    __tablename__ = "users"
    name: str = create_required_string_column(100)

# 4. 使用数据库
async def main():
    # 初始化数据库
    await db_manager.create_all_tables()
    
    # 使用数据库会话
    async with db_manager.get_session() as session:
        # 进行数据库操作
        pass

asyncio.run(main())
```

## 🎯 优势

1. **灵活性**: 外部调用方可以自由配置
2. **简洁性**: 不需要复杂的全局状态管理
3. **可测试性**: 每个测试可以使用不同的配置
4. **可维护性**: 配置和业务逻辑分离

## 📚 相关文档

- [PyAdvanceKit 配置管理文档](../docs/api-reference.md#配置管理)
- [数据库操作指南](../docs/quick-start.md#数据库操作)
- [示例代码](../examples/stage2_with_custom_config.py)

