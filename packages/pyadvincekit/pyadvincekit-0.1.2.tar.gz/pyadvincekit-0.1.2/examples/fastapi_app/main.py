"""
完整的FastAPI应用示例

展示如何使用PyAdvanceKit构建一个完整的Web API应用。
"""

import sys
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Query
from sqlalchemy import String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel as PydanticModel, Field

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pyadvincekit import (
    create_app, BaseModel, SoftDeleteModel, BaseCRUD,
    get_database, success_response, paginated_response,
    ResponseMessage, setup_all_middleware, Settings
)
from pyadvincekit.models.base import create_required_string_column, create_text_column
from pyadvincekit.core.exceptions import ValidationError, NotFoundError


# ================== 配置 ==================

settings = Settings(
    app_name="PyAdvanceKit 商店 API",
    app_version="1.0.0",
    environment="development",
    debug=True,
    database={
        "database_url": "sqlite+aiosqlite:///./shop.db",
        "echo_sql": True,
    }
)


# ================== 数据模型 ==================

class Category(BaseModel):
    """商品分类模型"""
    __tablename__ = "categories"
    
    name: Mapped[str] = create_required_string_column(100, unique=True, comment="分类名称")
    description: Mapped[Optional[str]] = create_text_column(comment="分类描述")


class Product(SoftDeleteModel):
    """商品模型（支持软删除）"""
    __tablename__ = "products"
    
    name: Mapped[str] = create_required_string_column(200, comment="商品名称")
    description: Mapped[Optional[str]] = create_text_column(comment="商品描述")
    price: Mapped[float] = mapped_column(Float, nullable=False, comment="价格")
    stock: Mapped[int] = mapped_column(Integer, default=0, comment="库存")
    category_id: Mapped[str] = mapped_column(String(36), nullable=False, comment="分类ID")


class Order(BaseModel):
    """订单模型"""
    __tablename__ = "orders"
    
    order_no: Mapped[str] = create_required_string_column(50, unique=True, comment="订单号")
    customer_name: Mapped[str] = create_required_string_column(100, comment="客户姓名")
    customer_email: Mapped[str] = create_required_string_column(255, comment="客户邮箱")
    total_amount: Mapped[float] = mapped_column(Float, nullable=False, comment="总金额")
    status: Mapped[str] = create_required_string_column(20, comment="订单状态")


# ================== Pydantic模型 ==================

class CategoryCreate(PydanticModel):
    name: str = Field(..., min_length=1, max_length=100, description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")


class CategoryUpdate(PydanticModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")


class ProductCreate(PydanticModel):
    name: str = Field(..., min_length=1, max_length=200, description="商品名称")
    description: Optional[str] = Field(None, description="商品描述")
    price: float = Field(..., gt=0, description="价格（必须大于0）")
    stock: int = Field(0, ge=0, description="库存（必须大于等于0）")
    category_id: str = Field(..., description="分类ID")


class ProductUpdate(PydanticModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="商品名称")
    description: Optional[str] = Field(None, description="商品描述")
    price: Optional[float] = Field(None, gt=0, description="价格（必须大于0）")
    stock: Optional[int] = Field(None, ge=0, description="库存（必须大于等于0）")
    category_id: Optional[str] = Field(None, description="分类ID")


class OrderCreate(PydanticModel):
    customer_name: str = Field(..., min_length=1, max_length=100, description="客户姓名")
    customer_email: str = Field(..., description="客户邮箱")
    items: List[dict] = Field(..., description="订单商品")


# ================== 服务层 ==================

class CategoryService:
    def __init__(self):
        self.crud = BaseCRUD(Category)
    
    async def create_category(self, data: CategoryCreate) -> Category:
        async with get_database() as db:
            # 检查分类名称是否已存在
            existing = await self.crud.get_multi(db, filters={"name": data.name})
            if existing:
                raise ValidationError("分类名称已存在", field="name")
            
            return await self.crud.create(db, data.model_dump())
    
    async def get_categories(self, skip: int = 0, limit: int = 50) -> tuple[List[Category], int]:
        async with get_database() as db:
            categories = await self.crud.get_multi(db, skip=skip, limit=limit)
            total = await self.crud.count(db)
            return categories, total
    
    async def get_category(self, category_id: str) -> Category:
        async with get_database() as db:
            category = await self.crud.get(db, category_id, raise_not_found=False)
            if not category:
                raise NotFoundError("分类不存在", resource_type="分类", resource_id=category_id)
            return category
    
    async def update_category(self, category_id: str, data: CategoryUpdate) -> Category:
        async with get_database() as db:
            category = await self.get_category(category_id)
            update_data = data.model_dump(exclude_unset=True)
            return await self.crud.update(db, category, update_data)
    
    async def delete_category(self, category_id: str) -> bool:
        async with get_database() as db:
            category = await self.get_category(category_id)
            return await self.crud.delete(db, category_id)


class ProductService:
    def __init__(self):
        self.crud = BaseCRUD(Product)
        self.category_service = CategoryService()
    
    async def create_product(self, data: ProductCreate) -> Product:
        async with get_database() as db:
            # 验证分类是否存在
            await self.category_service.get_category(data.category_id)
            
            return await self.crud.create(db, data.model_dump())
    
    async def get_products(
        self, 
        skip: int = 0, 
        limit: int = 20,
        category_id: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        search: Optional[str] = None
    ) -> tuple[List[Product], int]:
        async with get_database() as db:
            filters = {}
            
            if category_id:
                filters["category_id"] = category_id
            
            if min_price is not None:
                filters["price"] = {"operator": "gte", "value": min_price}
            
            if search:
                filters["name"] = {"operator": "like", "value": search}
            
            products = await self.crud.get_multi(
                db, skip=skip, limit=limit, filters=filters
            )
            total = await self.crud.count(db, filters=filters)
            return products, total
    
    async def get_product(self, product_id: str) -> Product:
        async with get_database() as db:
            product = await self.crud.get(db, product_id, raise_not_found=False)
            if not product:
                raise NotFoundError("商品不存在", resource_type="商品", resource_id=product_id)
            return product
    
    async def update_product(self, product_id: str, data: ProductUpdate) -> Product:
        async with get_database() as db:
            product = await self.get_product(product_id)
            
            # 如果更新分类，验证分类是否存在
            if data.category_id:
                await self.category_service.get_category(data.category_id)
            
            update_data = data.model_dump(exclude_unset=True)
            return await self.crud.update(db, product, update_data)
    
    async def delete_product(self, product_id: str) -> Product:
        async with get_database() as db:
            product = await self.get_product(product_id)
            return await self.crud.soft_delete(db, product_id)


class OrderService:
    def __init__(self):
        self.crud = BaseCRUD(Order)
        self.product_service = ProductService()
    
    async def create_order(self, data: OrderCreate) -> Order:
        import uuid
        from datetime import datetime
        
        # 计算订单总金额
        total_amount = 0.0
        for item in data.items:
            product = await self.product_service.get_product(item["product_id"])
            quantity = item["quantity"]
            
            if product.stock < quantity:
                raise ValidationError(f"商品 {product.name} 库存不足")
            
            total_amount += product.price * quantity
        
        # 生成订单号
        order_no = f"ORDER-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"
        
        async with get_database() as db:
            order_data = {
                "order_no": order_no,
                "customer_name": data.customer_name,
                "customer_email": data.customer_email,
                "total_amount": total_amount,
                "status": "pending"
            }
            
            order = await self.crud.create(db, order_data)
            
            # 更新商品库存
            for item in data.items:
                product = await self.product_service.get_product(item["product_id"])
                new_stock = product.stock - item["quantity"]
                await self.product_service.update_product(
                    product.id, 
                    ProductUpdate(stock=new_stock)
                )
            
            return order
    
    async def get_orders(self, skip: int = 0, limit: int = 20) -> tuple[List[Order], int]:
        async with get_database() as db:
            orders = await self.crud.get_multi(db, skip=skip, limit=limit)
            total = await self.crud.count(db)
            return orders, total


# ================== API路由 ==================

# 初始化服务
category_service = CategoryService()
product_service = ProductService()
order_service = OrderService()

# 分类路由
category_router = APIRouter(prefix="/categories", tags=["商品分类"])

@category_router.post("/")
async def create_category(data: CategoryCreate):
    category = await category_service.create_category(data)
    return success_response(category.to_dict(), ResponseMessage.CREATED)

@category_router.get("/")
async def get_categories(skip: int = 0, limit: int = 50):
    categories, total = await category_service.get_categories(skip, limit)
    items = [cat.to_dict() for cat in categories]
    page = (skip // limit) + 1
    return paginated_response(items, page, limit, total)

@category_router.get("/{category_id}")
async def get_category(category_id: str):
    category = await category_service.get_category(category_id)
    return success_response(category.to_dict())

@category_router.put("/{category_id}")
async def update_category(category_id: str, data: CategoryUpdate):
    category = await category_service.update_category(category_id, data)
    return success_response(category.to_dict(), ResponseMessage.UPDATED)

@category_router.delete("/{category_id}")
async def delete_category(category_id: str):
    success = await category_service.delete_category(category_id)
    return success_response({"deleted": success}, ResponseMessage.DELETED)


# 商品路由
product_router = APIRouter(prefix="/products", tags=["商品管理"])

@product_router.post("/")
async def create_product(data: ProductCreate):
    product = await product_service.create_product(data)
    return success_response(product.to_dict(), ResponseMessage.CREATED)

@product_router.get("/")
async def get_products(
    skip: int = 0,
    limit: int = 20,
    category_id: Optional[str] = Query(None, description="分类ID"),
    min_price: Optional[float] = Query(None, description="最低价格"),
    max_price: Optional[float] = Query(None, description="最高价格"),
    search: Optional[str] = Query(None, description="搜索关键词")
):
    products, total = await product_service.get_products(
        skip, limit, category_id, min_price, max_price, search
    )
    items = [product.to_dict() for product in products]
    page = (skip // limit) + 1
    return paginated_response(items, page, limit, total)

@product_router.get("/{product_id}")
async def get_product(product_id: str):
    product = await product_service.get_product(product_id)
    return success_response(product.to_dict())

@product_router.put("/{product_id}")
async def update_product(product_id: str, data: ProductUpdate):
    product = await product_service.update_product(product_id, data)
    return success_response(product.to_dict(), ResponseMessage.UPDATED)

@product_router.delete("/{product_id}")
async def delete_product(product_id: str):
    product = await product_service.delete_product(product_id)
    return success_response({"deleted": True}, ResponseMessage.DELETED)


# 订单路由
order_router = APIRouter(prefix="/orders", tags=["订单管理"])

@order_router.post("/")
async def create_order(data: OrderCreate):
    order = await order_service.create_order(data)
    return success_response(order.to_dict(), ResponseMessage.CREATED)

@order_router.get("/")
async def get_orders(skip: int = 0, limit: int = 20):
    orders, total = await order_service.get_orders(skip, limit)
    items = [order.to_dict() for order in orders]
    page = (skip // limit) + 1
    return paginated_response(items, page, limit, total)


# ================== 应用创建 ==================

app = create_app(
    settings=settings,
    title=settings.app_name,
    description="使用 PyAdvanceKit 构建的完整商店 API",
    version=settings.app_version,
    routers=[category_router, product_router, order_router],
    include_health_check=True,
    include_database_init=True
)

# 添加所有中间件
setup_all_middleware(app)


# ================== 启动函数 ==================

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动 PyAdvanceKit 商店 API")
    print(f"📖 API 文档: http://localhost:8000{app.docs_url}")
    print(f"🔍 ReDoc: http://localhost:8000{app.redoc_url}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

