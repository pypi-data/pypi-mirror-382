"""
通用CRUD操作基类

提供数据库增删改查的通用操作，支持类型安全和自动化处理。
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel as PydanticModel
from sqlalchemy import and_, asc, desc, func, or_, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select

from pyadvincekit.core.exceptions import (
    DatabaseError,
    NotFoundError,
    RecordNotFoundError,
    RecordAlreadyExistsError,
)
from pyadvincekit.models.base import BaseModel, SoftDeleteModel

from pyadvincekit.logging import get_logger

logger = get_logger(__name__)

# 泛型类型变量
ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=PydanticModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=PydanticModel)


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """通用CRUD操作基类"""

    def __init__(self, model: Type[ModelType]) -> None:
        """
        初始化CRUD操作类
        
        Args:
            model: SQLAlchemy模型类
        """
        self.model = model

    async def get(
        self, 
        db: AsyncSession, 
        id: Any,
        raise_not_found: bool = True
    ) -> Optional[ModelType]:
        """
        根据ID获取单个记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            raise_not_found: 是否在找不到记录时抛出异常
            
        Returns:
            模型实例或None
            
        Raises:
            RecordNotFoundError: 当记录不存在且raise_not_found为True时
        """
        try:
            result = await db.get(self.model, id)
            
            if result is None and raise_not_found:
                raise RecordNotFoundError(
                    f"{self.model.__name__} with id {id} not found",
                    model=self.model.__name__,
                    resource_id=str(id)
                )
            
            return result
            
        except Exception as e:
            if isinstance(e, RecordNotFoundError):
                raise
            logger.error(f"Failed to get {self.model.__name__} with id {id}: {e}")
            raise DatabaseError(f"Failed to retrieve record: {e}")

    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        filters: Optional[Dict[str, Any]] = None,
        include_deleted: bool = False
    ) -> List[ModelType]:
        """
        获取多个记录
        
        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 限制记录数
            order_by: 排序字段
            order_desc: 是否降序
            filters: 过滤条件
            include_deleted: 是否包含已删除记录（软删除模型）
            
        Returns:
            模型实例列表
        """
        try:
            query = select(self.model)
            
            # 处理软删除过滤
            if issubclass(self.model, SoftDeleteModel) and not include_deleted:
                query = query.where(self.model.is_deleted == False)
            
            # 处理过滤条件
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        if isinstance(value, list):
                            # 列表值使用IN查询
                            query = query.where(getattr(self.model, field).in_(value))
                        elif isinstance(value, dict) and "operator" in value:
                            # 复杂查询条件
                            column = getattr(self.model, field)
                            operator = value["operator"]
                            operand = value["value"]
                            
                            if operator == "like":
                                query = query.where(column.like(f"%{operand}%"))
                            elif operator == "ilike":
                                query = query.where(column.ilike(f"%{operand}%"))
                            elif operator == "gt":
                                query = query.where(column > operand)
                            elif operator == "gte":
                                query = query.where(column >= operand)
                            elif operator == "lt":
                                query = query.where(column < operand)
                            elif operator == "lte":
                                query = query.where(column <= operand)
                            elif operator == "ne":
                                query = query.where(column != operand)
                        else:
                            # 简单等值查询
                            query = query.where(getattr(self.model, field) == value)
            
            # 处理排序
            if order_by and hasattr(self.model, order_by):
                order_column = getattr(self.model, order_by)
                if order_desc:
                    query = query.order_by(desc(order_column))
                else:
                    query = query.order_by(asc(order_column))
            else:
                # 默认按创建时间降序
                if hasattr(self.model, 'created_at'):
                    query = query.order_by(desc(self.model.created_at))
            
            # 分页
            query = query.offset(skip).limit(limit)
            
            result = await db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Failed to get multiple {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to retrieve records: {e}")

    async def count(
        self,
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        include_deleted: bool = False
    ) -> int:
        """
        获取记录总数
        
        Args:
            db: 数据库会话
            filters: 过滤条件
            include_deleted: 是否包含已删除记录
            
        Returns:
            记录总数
        """
        try:
            query = select(func.count(self.model.id))
            
            # 处理软删除过滤
            if issubclass(self.model, SoftDeleteModel) and not include_deleted:
                query = query.where(self.model.is_deleted == False)
            
            # 处理过滤条件
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        query = query.where(getattr(self.model, field) == value)
            
            result = await db.execute(query)
            return result.scalar() or 0
            
        except Exception as e:
            logger.error(f"Failed to count {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to count records: {e}")

    async def create(
        self, 
        db: AsyncSession, 
        obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        创建新记录
        
        Args:
            db: 数据库会话
            obj_in: 输入数据（Pydantic模型或字典）
            
        Returns:
            创建的模型实例
        """
        try:
            if isinstance(obj_in, dict):
                create_data = obj_in
            else:
                create_data = obj_in.model_dump(exclude_unset=True)
            
            db_obj = self.model(**create_data)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            
            logger.info(f"Created {self.model.__name__} with id {db_obj.id}")
            return db_obj
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create {self.model.__name__}: {e}")
            
            # 检查是否为唯一约束冲突
            if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e):
                raise RecordAlreadyExistsError(f"{self.model.__name__} already exists")
            
            raise DatabaseError(f"Failed to create record: {e}")

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        更新记录
        
        Args:
            db: 数据库会话
            db_obj: 要更新的模型实例
            obj_in: 更新数据
            
        Returns:
            更新后的模型实例
        """
        try:
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.model_dump(exclude_unset=True)
            
            # 使用BaseModel的update_from_dict方法
            db_obj.update_from_dict(update_data)
            
            await db.commit()
            await db.refresh(db_obj)
            
            logger.info(f"Updated {self.model.__name__} with id {db_obj.id}")
            return db_obj
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to update record: {e}")

    async def update_by_id(
        self,
        db: AsyncSession,
        id: Any,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        根据ID更新记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            obj_in: 更新数据
            
        Returns:
            更新后的模型实例
        """
        db_obj = await self.get(db, id)
        return await self.update(db, db_obj, obj_in)

    async def delete(self, db: AsyncSession, id: Any) -> bool:
        """
        删除记录（物理删除）
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            是否删除成功
        """
        try:
            db_obj = await self.get(db, id)
            await db.delete(db_obj)
            await db.commit()
            
            logger.info(f"Deleted {self.model.__name__} with id {id}")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete {self.model.__name__} with id {id}: {e}")
            raise DatabaseError(f"Failed to delete record: {e}")

    async def soft_delete(self, db: AsyncSession, id: Any) -> ModelType:
        """
        软删除记录（仅对SoftDeleteModel有效）
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            软删除后的模型实例
        """
        if not issubclass(self.model, SoftDeleteModel):
            raise DatabaseError(f"{self.model.__name__} does not support soft delete")
        
        try:
            db_obj = await self.get(db, id)
            db_obj.soft_delete()
            await db.commit()
            await db.refresh(db_obj)
            
            logger.info(f"Soft deleted {self.model.__name__} with id {id}")
            return db_obj
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to soft delete {self.model.__name__} with id {id}: {e}")
            raise DatabaseError(f"Failed to soft delete record: {e}")

    async def restore(self, db: AsyncSession, id: Any) -> ModelType:
        """
        恢复软删除的记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            恢复后的模型实例
        """
        if not issubclass(self.model, SoftDeleteModel):
            raise DatabaseError(f"{self.model.__name__} does not support soft delete")
        
        try:
            # 包含已删除记录的查询
            query = select(self.model).where(self.model.id == id)
            result = await db.execute(query)
            db_obj = result.scalar_one_or_none()
            
            if not db_obj:
                raise RecordNotFoundError(f"{self.model.__name__} with id {id} not found")
            
            db_obj.restore()
            await db.commit()
            await db.refresh(db_obj)
            
            logger.info(f"Restored {self.model.__name__} with id {id}")
            return db_obj
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to restore {self.model.__name__} with id {id}: {e}")
            raise DatabaseError(f"Failed to restore record: {e}")

    async def exists(self, db: AsyncSession, id: Any) -> bool:
        """
        检查记录是否存在
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            是否存在
        """
        try:
            result = await self.get(db, id, raise_not_found=False)
            return result is not None
        except Exception as e:
            logger.error(f"Failed to check existence of {self.model.__name__} with id {id}: {e}")
            return False

    async def bulk_create(
        self, 
        db: AsyncSession, 
        objs_in: List[Union[CreateSchemaType, Dict[str, Any]]]
    ) -> List[ModelType]:
        """
        批量创建记录
        
        Args:
            db: 数据库会话
            objs_in: 输入数据列表
            
        Returns:
            创建的模型实例列表
        """
        try:
            db_objs = []
            for obj_in in objs_in:
                if isinstance(obj_in, dict):
                    create_data = obj_in
                else:
                    create_data = obj_in.model_dump(exclude_unset=True)
                
                db_obj = self.model(**create_data)
                db_objs.append(db_obj)
            
            db.add_all(db_objs)
            await db.commit()
            
            # 刷新所有对象
            for db_obj in db_objs:
                await db.refresh(db_obj)
            
            logger.info(f"Bulk created {len(db_objs)} {self.model.__name__} records")
            return db_objs
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to bulk create {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to bulk create records: {e}")


class CRUDBase(BaseCRUD[ModelType, PydanticModel, PydanticModel]):
    """简化的CRUD基类，不需要指定Schema类型"""
    pass
