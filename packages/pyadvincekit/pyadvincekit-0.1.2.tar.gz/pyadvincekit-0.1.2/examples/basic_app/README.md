# PyAdvanceKit 基础应用示例

这是一个使用 PyAdvanceKit 构建的完整示例应用，展示了框架的核心功能和最佳实践。

## 功能特性

- 🔧 **配置管理**: 多环境配置支持
- 👥 **用户管理**: 完整的用户CRUD操作
- 📦 **产品管理**: 支持软删除的产品管理
- 🛡️ **数据验证**: 输入数据验证和错误处理
- 📊 **数据库操作**: 异步数据库操作和查询
- 🏗️ **分层架构**: 清晰的业务逻辑分层

## 项目结构

```
basic_app/
├── app.py              # 主应用文件
├── requirements.txt    # 依赖配置
└── README.md          # 说明文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python app.py
```

### 3. 查看输出

应用将自动：
- 初始化SQLite数据库
- 创建用户和产品数据
- 演示各种数据库操作
- 展示错误处理机制

## 代码结构说明

### 配置管理

```python
app_settings = Settings(
    app_name="PyAdvanceKit 示例应用",
    environment="development",
    debug=True,
    database={
        "database_url": "sqlite+aiosqlite:///./example_app.db",
        "echo_sql": True,
    }
)
```

### 数据模型

```python
class User(BaseModel):
    """用户模型"""
    __tablename__ = "users"
    
    username: Mapped[str] = create_required_string_column(50, unique=True)
    email: Mapped[str] = create_required_string_column(255, unique=True)
    full_name: Mapped[str] = create_required_string_column(100)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

### 业务服务

```python
class UserService:
    """用户服务"""
    
    def __init__(self):
        self.crud = BaseCRUD(User)
    
    async def create_user(self, user_data: dict) -> User:
        # 数据验证
        if not user_data.get("username"):
            raise ValidationError("用户名不能为空", field="username")
        
        async with get_database() as db:
            return await self.crud.create(db, user_data)
```

## 核心功能演示

### 1. 用户管理

- 创建用户（带验证）
- 查询用户列表
- 更新用户信息
- 停用/激活用户
- 删除用户

### 2. 产品管理

- 创建产品
- 查询产品（支持分类、价格过滤）
- 更新产品信息
- 库存管理
- 软删除和恢复

### 3. 错误处理

- 数据验证错误
- 记录不存在错误
- 业务逻辑错误
- 统一错误处理

## 扩展建议

### 添加更多功能

1. **订单管理**: 添加订单模型和服务
2. **用户认证**: 集成JWT认证
3. **API接口**: 添加FastAPI路由
4. **数据迁移**: 使用Alembic管理数据库版本
5. **单元测试**: 添加pytest测试用例

### 生产环境配置

```python
# 生产环境配置示例
prod_settings = Settings(
    environment="production",
    debug=False,
    database={
        "database_url": "postgresql+asyncpg://user:pass@db:5432/prod_db",
        "pool_size": 20,
        "echo_sql": False,
    },
    logging={
        "log_level": "WARNING",
        "log_file_enabled": True,
        "log_file_path": "/var/log/app/app.log"
    }
)
```

## 性能优化建议

1. **连接池配置**: 根据负载调整数据库连接池大小
2. **查询优化**: 使用索引和合适的查询条件
3. **批量操作**: 对于大量数据使用批量创建/更新
4. **缓存策略**: 添加Redis缓存常用数据
5. **异步处理**: 充分利用异步特性处理并发

## 常见问题

### Q: 如何更换数据库？

A: 修改配置中的 `database_url` 并安装对应的驱动：

```python
# PostgreSQL
database_url = "postgresql+asyncpg://user:pass@localhost/db"

# MySQL  
database_url = "mysql+aiomysql://user:pass@localhost/db"
```

### Q: 如何添加新的模型？

A: 继承 `BaseModel` 或 `SoftDeleteModel`：

```python
class Category(BaseModel):
    __tablename__ = "categories"
    
    name: Mapped[str] = create_required_string_column(100)
    description: Mapped[str] = create_text_column()
```

### Q: 如何处理复杂查询？

A: 使用过滤器和自定义查询方法：

```python
# 复杂过滤
products = await product_crud.get_multi(
    db,
    filters={
        "price": {"operator": "between", "value": [100, 1000]},
        "category": "电子产品"
    }
)
```

## 更多示例

- [配置管理示例](../stage1_config_management.py)
- [数据库操作示例](../stage2_database_operations.py)

## 技术支持

如有问题，请查看：
- [项目文档](../../README.md)
- [开发计划](../../development_plan.md)
- [GitHub Issues](https://github.com/pyadvincekit/pyadvincekit/issues)

