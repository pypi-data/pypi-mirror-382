# PyAdvanceKit FastAPI 完整应用示例

这是一个使用 PyAdvanceKit 构建的完整的商店 API 应用，展示了框架的所有核心功能。

## 🎯 功能特性

- **商品分类管理**: 完整的分类 CRUD 操作
- **商品管理**: 支持软删除的商品管理，包含搜索和过滤
- **订单管理**: 订单创建和库存管理
- **统一响应格式**: 所有 API 返回标准格式
- **全局异常处理**: 自动处理各种异常并返回友好错误信息
- **请求日志**: 详细的请求日志记录
- **性能监控**: 自动监控 API 响应时间
- **API 文档**: 自动生成的 Swagger 文档

## 🚀 快速开始

### 1. 安装依赖

```bash
# 从项目根目录
pip install -r requirements.txt
pip install -e .
```

### 2. 运行应用

```bash
cd examples/fastapi_app
python main.py
```

### 3. 访问应用

- **API 文档**: http://localhost:8000/docs
- **ReDoc 文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## 📚 API 接口

### 商品分类 (`/categories`)

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/categories/` | 创建分类 |
| GET | `/categories/` | 获取分类列表 |
| GET | `/categories/{id}` | 获取分类详情 |
| PUT | `/categories/{id}` | 更新分类 |
| DELETE | `/categories/{id}` | 删除分类 |

### 商品管理 (`/products`)

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/products/` | 创建商品 |
| GET | `/products/` | 获取商品列表（支持搜索和过滤） |
| GET | `/products/{id}` | 获取商品详情 |
| PUT | `/products/{id}` | 更新商品 |
| DELETE | `/products/{id}` | 软删除商品 |

### 订单管理 (`/orders`)

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/orders/` | 创建订单 |
| GET | `/orders/` | 获取订单列表 |

## 🧪 测试示例

### 1. 创建分类

```bash
curl -X POST "http://localhost:8000/categories/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "电子产品",
       "description": "各种电子设备"
     }'
```

### 2. 创建商品

```bash
curl -X POST "http://localhost:8000/products/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "iPhone 15",
       "description": "苹果最新款手机",
       "price": 7999.0,
       "stock": 100,
       "category_id": "分类ID"
     }'
```

### 3. 搜索商品

```bash
curl "http://localhost:8000/products/?search=iPhone&min_price=5000&limit=10"
```

### 4. 创建订单

```bash
curl -X POST "http://localhost:8000/orders/" \
     -H "Content-Type: application/json" \
     -d '{
       "customer_name": "张三",
       "customer_email": "zhangsan@example.com",
       "items": [
         {
           "product_id": "商品ID",
           "quantity": 2
         }
       ]
     }'
```

## 📊 响应格式

### 成功响应

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "uuid",
    "name": "商品名称",
    ...
  }
}
```

### 分页响应

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [...],
    "meta": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "total_pages": 5,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### 错误响应

```json
{
  "code": 422,
  "message": "数据验证失败: name: 分类名称已存在",
  "data": null,
  "details": {
    "field": "name",
    "value": "重复的名称"
  }
}
```

## 🏗️ 项目结构

```
fastapi_app/
├── main.py              # 应用入口
├── README.md            # 说明文档
└── shop.db             # SQLite 数据库（自动创建）
```

## 🔧 配置说明

应用使用以下配置：

```python
settings = Settings(
    app_name="PyAdvanceKit 商店 API",
    app_version="1.0.0",
    environment="development",
    debug=True,
    database={
        "database_url": "sqlite+aiosqlite:///./shop.db",
        "echo_sql": True,  # 开发环境显示 SQL
    }
)
```

## 🛠️ 核心特性展示

### 1. 统一响应格式

所有 API 都返回标准格式，无需手动处理：

```python
@category_router.post("/")
async def create_category(data: CategoryCreate):
    category = await category_service.create_category(data)
    return success_response(category.to_dict(), ResponseMessage.CREATED)
```

### 2. 全局异常处理

自动捕获和处理各种异常：

```python
# 业务逻辑中只需抛出异常
if existing:
    raise ValidationError("分类名称已存在", field="name")

# 框架自动转换为标准错误响应
```

### 3. 软删除支持

商品支持软删除，保护数据安全：

```python
class Product(SoftDeleteModel):  # 继承软删除模型
    # ... 字段定义

# 软删除操作
await self.crud.soft_delete(db, product_id)
```

### 4. 高级查询功能

支持复杂的查询条件：

```python
# 支持搜索、价格范围、分类过滤
products, total = await product_service.get_products(
    skip=0, limit=20,
    category_id="分类ID",
    min_price=100.0,
    search="iPhone"
)
```

### 5. 中间件集成

自动添加请求日志、性能监控等功能：

```python
# 一行代码添加所有推荐中间件
setup_all_middleware(app)
```

## 🚨 错误处理示例

应用会自动处理以下错误情况：

1. **数据验证错误**: 请求数据格式不正确
2. **业务逻辑错误**: 分类名称重复、库存不足等
3. **资源不存在**: 查询不存在的商品或分类
4. **数据库错误**: 连接失败、约束冲突等
5. **服务器错误**: 未处理的异常

## 📈 性能特性

- **异步操作**: 所有数据库操作都是异步的
- **连接池**: 自动管理数据库连接池
- **请求追踪**: 每个请求都有唯一 ID 便于调试
- **性能监控**: 自动记录慢请求

## 🔍 日志示例

```
2024-09-17 12:00:00 - INFO - 请求开始: POST /products/
2024-09-17 12:00:00 - INFO - 用户创建成功: iPhone 15
2024-09-17 12:00:00 - INFO - 请求完成: POST /products/ - 200 (0.050s)
```

## 🚀 生产环境部署

### 1. 环境变量配置

```bash
export PYADVINCEKIT_ENVIRONMENT=production
export PYADVINCEKIT_DATABASE_URL="postgresql://user:pass@host:5432/shop_db"
export PYADVINCEKIT_DEBUG=false
```

### 2. 使用 Gunicorn

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 3. Docker 部署

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📞 更多信息

- 查看 [项目根目录 README](../../README.md) 了解更多功能
- 查看 [开发计划](../../development_plan.md) 了解架构设计
- 参考 [其他示例](../) 学习具体功能

---

**这个示例展示了 PyAdvanceKit 的强大功能，帮助您快速构建生产就绪的 Web API！** 🎉

