# PyAdvanceKit .env 配置指南

本指南展示如何在外部项目中使用 PyAdvanceKit 的 `.env` 配置功能。

## 1. 基本使用

### 1.1 创建 .env 文件

在你的项目根目录创建 `.env` 文件：

```bash
# 复制模板文件
cp env_config_example.txt .env
```

### 1.2 最简单的使用方式

```python
from pyadvincekit import create_app_from_env

# 自动查找 .env 文件并创建应用
app = create_app_from_env(
    app_title="我的应用",
    app_description="使用 .env 配置的应用"
)

# 添加路由
@app.get("/")
async def root():
    return {"message": "Hello from PyAdvanceKit!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 2. 配置选项

### 2.1 应用基础配置

```bash
# .env 文件
PYADVINCEKIT_APP_NAME=我的应用
PYADVINCEKIT_DEBUG=true
PYADVINCEKIT_ENVIRONMENT=development
```

### 2.2 数据库配置

```bash
# SQLite 数据库
PYADVINCEKIT_DATABASE_URL=sqlite:///./my_app.db

# MySQL 数据库
PYADVINCEKIT_DATABASE_URL=mysql://root:password@localhost:3306/my_database

# PostgreSQL 数据库
PYADVINCEKIT_DATABASE_URL=postgresql://user:password@localhost:5432/my_database
```

### 2.3 日志配置

```bash
PYADVINCEKIT_LOG_LEVEL=INFO
PYADVINCEKIT_LOG_FILE_ENABLED=true
PYADVINCEKIT_LOG_FILE_PATH=logs/my_app.log
PYADVINCEKIT_STRUCTURED_LOGGING=true
```

### 2.4 JWT 认证配置

```bash
PYADVINCEKIT_JWT_SECRET_KEY=your-super-secret-jwt-key
PYADVINCEKIT_JWT_ALGORITHM=HS256
PYADVINCEKIT_JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 3. 高级使用

### 3.1 使用配置管理器

```python
from pyadvincekit import ConfigManager

# 创建配置管理器
config_manager = ConfigManager(".env")

# 设置配置
settings = config_manager.setup_pyadvincekit()

# 创建应用
app = config_manager.create_app_with_config(
    app_title="我的应用",
    app_description="使用配置管理器的应用"
)
```

### 3.2 自定义配置

```python
from pyadvincekit import setup_from_env_file

# 自定义配置
custom_settings = {
    "APP_NAME": "自定义应用",
    "DEBUG": True,
    "DATABASE_URL": "sqlite:///./custom.db",
    "LOG_LEVEL": "DEBUG"
}

# 设置配置
settings = setup_from_env_file(".env", custom_settings)
```

### 3.3 环境变量覆盖

```python
import os
from pyadvincekit import reload_settings

# 设置环境变量（会覆盖 .env 文件）
os.environ["PYADVINCEKIT_APP_NAME"] = "环境变量覆盖的应用"
os.environ["PYADVINCEKIT_DEBUG"] = "false"

# 重新加载配置
settings = reload_settings()
```

## 4. 配置优先级

配置的优先级从高到低：

1. **环境变量** - 最高优先级
2. **程序化配置** - 通过代码设置的配置
3. **`.env` 文件** - 文件中的配置
4. **默认配置** - PyAdvanceKit 的默认值

## 5. 完整示例

### 5.1 项目结构

```
my_project/
├── .env                 # 配置文件
├── main.py             # 主应用文件
├── requirements.txt    # 依赖文件
└── logs/              # 日志目录（自动创建）
```

### 5.2 main.py

```python
from pyadvincekit import create_app_from_env, init_database
import asyncio

# 创建应用
app = create_app_from_env(
    app_title="我的 PyAdvanceKit 应用",
    app_description="使用 .env 配置的完整应用",
    app_version="1.0.0"
)

# 添加路由
@app.get("/")
async def root():
    return {"message": "欢迎使用 PyAdvanceKit!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# 启动时初始化数据库
@app.on_event("startup")
async def startup():
    await init_database()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 5.3 .env 文件

```bash
# 应用配置
PYADVINCEKIT_APP_NAME=我的 PyAdvanceKit 应用
PYADVINCEKIT_DEBUG=true
PYADVINCEKIT_ENVIRONMENT=development

# 数据库配置
PYADVINCEKIT_DATABASE_URL=sqlite:///./my_app.db

# 日志配置
PYADVINCEKIT_LOG_LEVEL=INFO
PYADVINCEKIT_LOG_FILE_ENABLED=true
PYADVINCEKIT_LOG_FILE_PATH=logs/my_app.log

# JWT 配置
PYADVINCEKIT_JWT_SECRET_KEY=my-super-secret-jwt-key-change-in-production
```

### 5.4 requirements.txt

```txt
pyadvincekit
uvicorn
python-dotenv
```

## 6. 部署配置

### 6.1 生产环境

```bash
# 生产环境 .env
PYADVINCEKIT_APP_NAME=生产应用
PYADVINCEKIT_DEBUG=false
PYADVINCEKIT_ENVIRONMENT=production
PYADVINCEKIT_DATABASE_URL=postgresql://user:pass@db:5432/prod_db
PYADVINCEKIT_LOG_LEVEL=WARNING
PYADVINCEKIT_JWT_SECRET_KEY=production-secret-key
```

### 6.2 Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# 使用环境变量配置
ENV PYADVINCEKIT_APP_NAME=我的应用
ENV PYADVINCEKIT_ENVIRONMENT=production
ENV PYADVINCEKIT_DATABASE_URL=postgresql://user:pass@db:5432/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 7. 故障排除

### 7.1 常见问题

1. **`.env` 文件未生效**
   - 检查文件路径是否正确
   - 确保使用 `PYADVINCEKIT_` 前缀
   - 调用 `reload_settings()` 重新加载

2. **配置冲突**
   - 检查环境变量是否覆盖了 `.env` 文件
   - 使用 `get_settings()` 查看当前配置

3. **数据库连接失败**
   - 检查数据库 URL 格式
   - 确保数据库服务正在运行

### 7.2 调试配置

```python
from pyadvincekit import get_settings

# 查看当前配置
settings = get_settings()
print(f"应用名称: {settings.app_name}")
print(f"数据库URL: {settings.database.database_url}")
print(f"日志级别: {settings.logging.log_level}")
```

## 8. 最佳实践

1. **安全性**
   - 不要在 `.env` 文件中存储敏感信息
   - 使用环境变量存储生产环境的密钥

2. **版本控制**
   - 将 `.env.example` 加入版本控制
   - 将 `.env` 加入 `.gitignore`

3. **配置管理**
   - 为不同环境创建不同的配置文件
   - 使用配置验证确保配置正确性

4. **日志记录**
   - 启用结构化日志便于分析
   - 设置合适的日志级别