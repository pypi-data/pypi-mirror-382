# PyAdvanceKit 安装指南

## 📋 系统要求

- **Python**: 3.8+
- **操作系统**: Windows/Linux/macOS
- **内存**: 最少 512MB
- **磁盘空间**: 100MB+

## 🚀 快速安装

### 方式一：PyPI 安装（推荐）

```bash
# 基础安装
pip install pyadvincekit

# 包含所有数据库驱动
pip install "pyadvincekit[all]"

# 包含特定数据库驱动
pip install "pyadvincekit[postgresql]"  # PostgreSQL
pip install "pyadvincekit[mysql]"       # MySQL
pip install "pyadvincekit[sqlite]"      # SQLite
```

### 方式二：源码安装

```bash
# 克隆项目
git clone https://github.com/pyadvincekit/pyadvincekit.git
cd pyadvincekit

# 安装依赖
pip install -r requirements.txt

# 开发模式安装
pip install -e .
```

## 🔧 环境配置

### 开发环境

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 或者使用自动安装脚本
python scripts/install_dev_deps.py

# 设置pre-commit钩子
pre-commit install

# 运行测试
pytest

# 运行异步测试
pytest --asyncio-mode=auto

# 代码格式化
black .
isort .
```

### 生产环境

```bash
# 安装生产依赖
pip install -r requirements-prod.txt

# 设置环境变量
export PYADVINCEKIT_ENVIRONMENT=production
export PYADVINCEKIT_DATABASE_URL="postgresql://user:pass@host:5432/db"
```

## 📊 数据库配置

### SQLite（开发环境推荐）

```bash
# 安装SQLite驱动
pip install aiosqlite

# 配置（无需额外设置）
DATABASE_URL="sqlite+aiosqlite:///./app.db"
```

### PostgreSQL（生产环境推荐）

```bash
# 安装PostgreSQL驱动
pip install asyncpg psycopg2-binary

# 配置
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/dbname"
```

### MySQL

```bash
# 安装MySQL驱动
pip install aiomysql pymysql

# 配置
DATABASE_URL="mysql+aiomysql://user:password@localhost:3306/dbname"
```

## 🐳 Docker 安装

### 使用 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYADVINCEKIT_ENVIRONMENT=production
      - PYADVINCEKIT_DATABASE_URL=postgresql://user:pass@db:5432/app
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=app
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Dockerfile 示例

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYADVINCEKIT_ENVIRONMENT=production

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## ⚡ 虚拟环境

### 使用 venv

```bash
# 创建虚拟环境
python -m venv pyadvincekit-env

# 激活虚拟环境
# Windows
pyadvincekit-env\Scripts\activate
# Linux/macOS
source pyadvincekit-env/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 使用 conda

```bash
# 创建环境
conda create -n pyadvincekit python=3.11

# 激活环境
conda activate pyadvincekit

# 安装依赖
pip install -r requirements.txt
```

## 🔍 验证安装

### 基础验证

```python
# 验证安装
python -c "import pyadvincekit; print(f'PyAdvanceKit {pyadvincekit.__version__} 安装成功!')"

# 验证配置
python -c "from pyadvincekit import Settings; s=Settings(); print(f'配置加载成功: {s.app_name}')"

# 验证数据库
python -c "from pyadvincekit import get_database; print('数据库模块加载成功')"
```

### 完整测试

```bash
# 运行示例
cd examples
python stage1_config_management.py
python stage2_database_operations.py

# 运行基础应用
cd basic_app
python app.py
```

## 🚨 常见问题

### 异步测试问题

如果遇到异步测试相关的错误，如：
```
You need to install a suitable plugin for your async framework
```

**解决方案：**

1. **安装异步测试插件：**
```bash
pip install pytest-asyncio pytest-tornasync pytest-trio pytest-twisted
```

2. **使用自动安装脚本：**
```bash
python scripts/install_dev_deps.py
```

3. **运行异步测试：**
```bash
# 使用 asyncio 模式
pytest --asyncio-mode=auto

# 或者直接运行异步示例
python examples/stage3_fastapi_integration.py
```

4. **检查 Python 版本：**
确保使用 Python 3.8+ 版本，因为早期版本对 asyncio 支持不完整。

### 安装问题

**Q: pip install 失败？**

```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pyadvincekit

# 忽略缓存
pip install --no-cache-dir pyadvincekit
```

**Q: 编译错误？**

```bash
# 安装编译工具
# Ubuntu/Debian
sudo apt-get install build-essential python3-dev

# CentOS/RHEL
sudo yum install gcc python3-devel

# Windows
# 安装 Microsoft C++ Build Tools
```

### 数据库问题

**Q: PostgreSQL连接失败？**

```python
# 检查连接字符串
DATABASE_URL = "postgresql+asyncpg://user:pass@host:5432/db"

# 检查防火墙和网络
telnet host 5432

# 检查数据库是否存在
psql -h host -U user -d db -c "SELECT version();"
```

**Q: SQLite权限问题？**

```bash
# 检查目录权限
ls -la ./

# 创建数据库目录
mkdir -p data
chmod 755 data
```

### 导入问题

**Q: ModuleNotFoundError？**

```bash
# 检查安装
pip list | grep pyadvincekit

# 重新安装
pip uninstall pyadvincekit
pip install pyadvincekit

# 检查Python路径
python -c "import sys; print(sys.path)"
```

## 📞 获取帮助

- 📖 **文档**: [GitHub Wiki](https://github.com/pyadvincekit/pyadvincekit/wiki)
- 🐛 **问题报告**: [GitHub Issues](https://github.com/pyadvincekit/pyadvincekit/issues)
- 💬 **讨论**: [GitHub Discussions](https://github.com/pyadvincekit/pyadvincekit/discussions)
- 📧 **邮箱**: team@pyadvincekit.com

## 🔄 更新

### 检查更新

```bash
# 检查当前版本
pip show pyadvincekit

# 检查最新版本
pip index versions pyadvincekit

# 更新到最新版本
pip install --upgrade pyadvincekit
```

### 迁移指南

查看 [CHANGELOG.md](./CHANGELOG.md) 了解版本变更和迁移说明。

---

**安装完成后，查看 [examples/](./examples/) 目录开始您的 PyAdvanceKit 之旅！** 🚀
