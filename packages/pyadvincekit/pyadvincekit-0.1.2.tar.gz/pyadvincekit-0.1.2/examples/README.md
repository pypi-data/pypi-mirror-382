# PyAdvanceKit 示例集合

欢迎来到 PyAdvanceKit 示例集合！这里包含了各种实用的示例，帮助您快速上手并掌握框架的各项功能。

## 📁 示例目录

### 🚀 快速开始

| 示例 | 描述 | 难度 | 预计时间 |
|------|------|------|----------|
| [基础应用](./basic_app/) | 完整的示例应用，展示核心功能 | ⭐⭐ | 15分钟 |

### 📚 分阶段学习

| 示例 | 功能模块 | 描述 | 难度 |
|------|----------|------|------|
| [阶段一：配置管理](./stage1_config_management.py) | 配置系统 | 多环境配置、环境变量、验证 | ⭐ |
| [阶段二：数据库操作](./stage2_database_operations.py) | 数据库 | 模型定义、CRUD、查询、软删除 | ⭐⭐ |

### 🔧 高级应用（即将推出）

| 示例 | 功能模块 | 描述 | 状态 |
|------|----------|------|------|
| FastAPI 集成 | Web框架 | API路由、中间件、文档 | 🚧 开发中 |
| 认证授权 | 安全 | JWT、权限控制、用户管理 | 📋 计划中 |
| 微服务架构 | 架构 | 服务拆分、通信、部署 | 📋 计划中 |

## 🎯 学习路径推荐

### 新手入门 (30分钟)
1. ⏰ **5分钟**: 阅读 [项目README](../README.md) 了解整体概况
2. ⏰ **10分钟**: 运行 [阶段一：配置管理](./stage1_config_management.py)
3. ⏰ **15分钟**: 运行 [基础应用示例](./basic_app/)

### 深入学习 (1小时)
1. ⏰ **20分钟**: 详细学习 [阶段二：数据库操作](./stage2_database_operations.py)
2. ⏰ **20分钟**: 自定义基础应用中的模型和业务逻辑
3. ⏰ **20分钟**: 阅读 [开发计划](../development_plan.md) 了解架构设计

### 实战应用 (2小时+)
1. 基于基础应用示例，构建您自己的业务应用
2. 集成到现有项目中
3. 根据需求扩展功能模块

## 🛠️ 运行环境准备

### 基础要求
- Python 3.8+
- 基础Python异步编程知识

### 安装步骤

1. **克隆项目**（如果还没有）
   ```bash
   git clone https://github.com/pyadvincekit/pyadvincekit.git
   cd pyadvincekit
   ```

2. **安装基础包**
   ```bash
   pip install -e .
   ```

3. **运行示例**
   ```bash
   # 配置管理示例
   python examples/stage1_config_management.py
   
   # 数据库操作示例  
   python examples/stage2_database_operations.py
   
   # 基础应用示例
   cd examples/basic_app
   python app.py
   ```

## 📖 示例详细说明

### 阶段一：配置管理示例

**文件**: `stage1_config_management.py`

**学习内容**:
- ✅ 基础配置使用
- ✅ 多环境配置切换
- ✅ 环境变量覆盖
- ✅ 配置验证机制
- ✅ 数据库URL自动转换
- ✅ 配置文件最佳实践

**运行输出**: 展示各种配置场景的使用方法和结果

**适用场景**: 项目初始化、环境配置、部署配置

### 阶段二：数据库操作示例

**文件**: `stage2_database_operations.py`

**学习内容**:
- ✅ 数据库模型定义（BaseModel、SoftDeleteModel）
- ✅ 基础CRUD操作（增删改查）
- ✅ 高级查询（过滤、排序、分页）
- ✅ 软删除功能使用
- ✅ 批量操作优化
- ✅ 模型方法和字典转换
- ✅ 复杂业务场景处理

**运行输出**: 完整演示所有数据库操作，包含详细的操作步骤和结果

**适用场景**: 数据层设计、CRUD接口开发、数据查询优化

### 基础应用示例

**目录**: `basic_app/`

**学习内容**:
- ✅ 完整应用架构设计
- ✅ 业务逻辑分层（Service层）
- ✅ 数据验证和错误处理
- ✅ 多模型关联操作
- ✅ 生产级代码组织
- ✅ 配置管理最佳实践

**包含文件**:
- `app.py`: 主应用逻辑
- `requirements.txt`: 依赖配置
- `README.md`: 详细说明

**适用场景**: 项目脚手架、业务系统开发、代码规范参考

## 💡 最佳实践提示

### 配置管理
- ✅ 使用环境变量管理敏感配置
- ✅ 不同环境使用不同配置文件
- ✅ 利用配置验证避免启动时错误

### 数据库操作
- ✅ 优先使用软删除保护数据
- ✅ 合理使用批量操作提升性能
- ✅ 添加适当的数据验证
- ✅ 使用事务确保数据一致性

### 代码组织
- ✅ 按功能模块组织代码
- ✅ 分离业务逻辑和数据层
- ✅ 统一异常处理机制
- ✅ 添加适当的日志记录

## 🔧 自定义和扩展

### 添加新模型
```python
class YourModel(BaseModel):
    __tablename__ = "your_table"
    
    field1: Mapped[str] = create_required_string_column(100)
    field2: Mapped[int] = mapped_column(Integer, default=0)
```

### 创建服务类
```python
class YourService:
    def __init__(self):
        self.crud = BaseCRUD(YourModel)
    
    async def your_business_method(self):
        async with get_database() as db:
            return await self.crud.get_multi(db)
```

### 添加数据验证
```python
def validate_data(data: dict):
    if not data.get("required_field"):
        raise ValidationError("字段不能为空", field="required_field")
```

## 🚨 常见问题解决

### 导入错误
```bash
# 确保正确安装
pip install -e .

# 或者添加到Python路径
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 数据库连接问题
```python
# 检查数据库URL格式
database_url = "sqlite+aiosqlite:///./test.db"  # SQLite
database_url = "postgresql+asyncpg://user:pass@host/db"  # PostgreSQL
```

### 异步编程问题
```python
# 确保在异步环境中运行
import asyncio

async def main():
    # 您的异步代码
    pass

if __name__ == "__main__":
    asyncio.run(main())
```

## 📞 获取帮助

- 📖 **文档**: [项目README](../README.md)
- 🐛 **问题反馈**: [GitHub Issues](https://github.com/pyadvincekit/pyadvincekit/issues)
- 💬 **讨论**: [GitHub Discussions](https://github.com/pyadvincekit/pyadvincekit/discussions)
- 📧 **邮箱**: team@pyadvincekit.com

## 🎯 下一步

1. **完成所有示例学习** - 掌握框架核心功能
2. **参考基础应用** - 了解最佳实践
3. **开始实际项目** - 应用到真实业务场景
4. **关注项目更新** - 获取最新功能和改进
5. **参与社区贡献** - 分享经验和建议

---

**开始您的 PyAdvanceKit 之旅吧！** 🚀

任何问题都欢迎在社区中提出，我们会积极帮助您解决。

