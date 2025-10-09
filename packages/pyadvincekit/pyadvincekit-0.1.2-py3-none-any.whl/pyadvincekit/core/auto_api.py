"""
自动 API 生成器

基于模型自动生成统一POST风格的API接口。
所有业务接口都使用POST方法，不遵循RESTful规范。
"""

from typing import Type, List, Optional, Dict, Any, Union
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel as PydanticModel, create_model
from sqlalchemy.orm import Mapped
from sqlalchemy import Column

from pyadvincekit.models.base import BaseModel, SoftDeleteModel
from pyadvincekit.crud.base import BaseCRUD
from pyadvincekit.core.response import success_response, error_response, paginated_response, ResponseCode, ResponseMessage
from pyadvincekit.core.database import get_database
from pyadvincekit.core.exceptions import RecordNotFoundError, RecordAlreadyExistsError
from pyadvincekit.schemas.common import (
    GetByIdRequest, QueryRequest, DeleteRequest, UpdateRequest, CountRequest,
    ExistsRequest, RestoreRequest, BulkCreateRequest, BatchDeleteRequest
)

from pyadvincekit.logging import get_logger

logger = get_logger(__name__)


class AutoAPIGenerator:
    """自动 API 生成器"""
    
    def __init__(self, prefix: str = "/api", tags: Optional[List[str]] = None):
        self.prefix = prefix
        self.tags = tags or []
        self.generated_routers: Dict[str, APIRouter] = {}
    
    def generate_api(
        self,
        model_class: Type[BaseModel],
        crud_class: Optional[Type[BaseCRUD]] = None,
        router_prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        include_endpoints: Optional[List[str]] = None
    ) -> APIRouter:
        """
        为模型自动生成统一POST风格的API接口
        
        Args:
            model_class: 模型类
            crud_class: CRUD 类，如果为 None 则自动创建
            router_prefix: 路由前缀，默认为模型名称的小写复数形式
            tags: API 标签
            include_endpoints: 包含的端点列表，默认为所有端点
            
        Returns:
            APIRouter: 生成的路由器
        """
        if crud_class is None:
            # 创建默认的 CRUD 类
            class DefaultCRUD(BaseCRUD[model_class, dict, dict]):
                pass
            crud_class = DefaultCRUD
        
        if router_prefix is None:
            router_prefix = f"/{model_class.__tablename__}"
        
        if tags is None:
            tags = [model_class.__name__]
        
        if include_endpoints is None:
            include_endpoints = ["query", "get", "create", "update", "delete", "count"]
            if issubclass(model_class, SoftDeleteModel):
                include_endpoints.extend(["soft_delete", "restore"])
        
        # 生成 Pydantic 模型
        create_model_class, update_model_class = self._generate_pydantic_models(model_class)
        
        # 创建路由器
        router = APIRouter(prefix=router_prefix, tags=tags)
        
        # 生成 CRUD 实例
        crud_instance = crud_class(model_class)
        
        # 生成各个POST端点
        if "query" in include_endpoints:
            router.add_api_route(
                "/query",
                self._create_query_endpoint(crud_instance, model_class),
                methods=["POST"],
                response_model=None,
                summary=f"查询{model_class.__name__}列表",
                description=f"分页查询{model_class.__name__}列表，支持过滤和搜索"
            )
        
        if "get" in include_endpoints:
            router.add_api_route(
                "/get",
                self._create_get_endpoint(crud_instance, model_class),
                methods=["POST"],
                response_model=None,
                summary=f"获取{model_class.__name__}详情",
                description=f"根据ID获取{model_class.__name__}详情"
            )
        
        if "create" in include_endpoints:
            router.add_api_route(
                "/create",
                self._create_create_endpoint(crud_instance, model_class, create_model_class),
                methods=["POST"],
                response_model=None,
                status_code=status.HTTP_201_CREATED,
                summary=f"创建{model_class.__name__}",
                description=f"创建新的{model_class.__name__}记录"
            )
        
        if "update" in include_endpoints:
            router.add_api_route(
                "/update",
                self._create_update_endpoint(crud_instance, model_class, update_model_class),
                methods=["POST"],
                response_model=None,
                summary=f"更新{model_class.__name__}",
                description=f"根据ID更新{model_class.__name__}记录"
            )
        
        if "delete" in include_endpoints:
            router.add_api_route(
                "/delete",
                self._create_delete_endpoint(crud_instance, model_class),
                methods=["POST"],
                response_model=None,
                status_code=status.HTTP_204_NO_CONTENT,
                summary=f"删除{model_class.__name__}",
                description=f"根据ID删除{model_class.__name__}记录"
            )
        
        if "count" in include_endpoints:
            router.add_api_route(
                "/count",
                self._create_count_endpoint(crud_instance, model_class),
                methods=["POST"],
                response_model=None,
                summary=f"统计{model_class.__name__}数量",
                description=f"统计{model_class.__name__}记录数量"
            )
        
        # 如果是软删除模型，添加软删除相关端点
        if issubclass(model_class, SoftDeleteModel):
            if "soft_delete" in include_endpoints:
                router.add_api_route(
                    "/soft-delete",
                    self._create_soft_delete_endpoint(crud_instance, model_class),
                    methods=["POST"],
                    response_model=None,
                    summary=f"软删除{model_class.__name__}",
                    description=f"根据ID软删除{model_class.__name__}记录"
                )
            
            if "restore" in include_endpoints:
                router.add_api_route(
                    "/restore",
                    self._create_restore_endpoint(crud_instance, model_class),
                    methods=["POST"],
                    response_model=None,
                    summary=f"恢复{model_class.__name__}",
                    description=f"根据ID恢复{model_class.__name__}记录"
                )
        
        # 保存生成的路由器
        self.generated_routers[model_class.__name__] = router
        
        logger.info(f"Generated API for {model_class.__name__} with prefix {router_prefix}")
        
        return router
    
    def _generate_pydantic_models(self, model_class: Type[BaseModel]) -> tuple:
        """生成 Pydantic 模型"""
        
        # 获取模型字段
        fields = {}
        update_fields = {}
        
        for column_name, column in model_class.__table__.columns.items():
            # 跳过主键和自动生成的字段
            if column_name in ['id', 'created_at', 'updated_at', 'is_deleted', 'deleted_at']:
                continue
            
            # 获取字段类型
            python_type = self._get_python_type(column)
            
            # 创建字段
            if column.nullable:
                fields[column_name] = (Optional[python_type], None)
                update_fields[column_name] = (Optional[python_type], None)
            else:
                fields[column_name] = (python_type, ...)
                update_fields[column_name] = (Optional[python_type], None)
        
        # 创建 Pydantic 模型
        create_model_class = create_model(
            f"{model_class.__name__}Create",
            **fields
        )
        
        update_model_class = create_model(
            f"{model_class.__name__}Update",
            **update_fields
        )
        
        return create_model_class, update_model_class
    
    def _get_python_type(self, column: Column) -> Type:
        """获取 Python 类型"""
        from sqlalchemy import String, Integer, Boolean, Float, DateTime, Text
        
        if isinstance(column.type, String):
            return str
        elif isinstance(column.type, Integer):
            return int
        elif isinstance(column.type, Boolean):
            return bool
        elif isinstance(column.type, Float):
            return float
        elif isinstance(column.type, DateTime):
            from datetime import datetime
            return datetime
        elif isinstance(column.type, Text):
            return str
        else:
            return str
    
    def _create_query_endpoint(self, crud_instance: BaseCRUD, model_class: Type[BaseModel]):
        """创建查询端点（POST方法）"""
        
        async def query_items(request: QueryRequest):
            try:
                async with get_database() as session:
                    # 计算跳过的记录数
                    skip = (request.page - 1) * request.size
                    
                    # 查询数据
                    items = await crud_instance.get_multi(
                        session,
                        skip=skip,
                        limit=request.size,
                        filters=request.filters,
                        order_by=request.order_by,
                        order_desc=request.order_desc,
                        include_deleted=request.include_deleted
                    )
                    
                    # 获取总数
                    total = await crud_instance.count(
                        session,
                        filters=request.filters,
                        include_deleted=request.include_deleted
                    )
                    
                    # 返回分页响应
                    return paginated_response(
                        items=[item.to_dict() for item in items],
                        page=request.page,
                        page_size=request.size,
                        total=total,
                        message=ResponseMessage.QUERIED,
                        ret_code=ResponseCode.SUCCESS
                    )
            except Exception as e:
                logger.error(f"Query {model_class.__name__} failed: {e}")
                return error_response(
                    message=f"查询{model_class.__name__}失败: {str(e)}",
                    ret_code=ResponseCode.BUSINESS_ERROR
                )
        
        return query_items
    
    def _create_create_endpoint(self, crud_instance: BaseCRUD, model_class: Type[BaseModel], create_model_class):
        """创建创建端点"""
        
        async def create_item(item_data: create_model_class):
            async with get_database() as session:
                try:
                    item = await crud_instance.create(session, item_data.dict())
                    return success_response(data=item.to_dict())
                except RecordAlreadyExistsError as e:
                    return error_response(str(e), code=409)
                except Exception as e:
                    return error_response(f"创建失败: {str(e)}", code=500)
        
        return create_item
    
    def _create_get_endpoint(self, crud_instance: BaseCRUD, model_class: Type[BaseModel]):
        """创建获取端点（POST方法）"""
        
        async def get_item(request: GetByIdRequest):
            try:
                async with get_database() as session:
                    item = await crud_instance.get(session, request.id)
                    return success_response(
                        data=item.to_dict(),
                        message=ResponseMessage.QUERIED,
                        ret_code=ResponseCode.SUCCESS
                    )
            except RecordNotFoundError:
                return error_response(
                    message=f"{model_class.__name__}不存在",
                    ret_code=ResponseCode.NOT_FOUND,
                    http_status=404
                )
            except Exception as e:
                logger.error(f"Get {model_class.__name__} failed: {e}")
                return error_response(
                    message=f"获取{model_class.__name__}失败: {str(e)}",
                    ret_code=ResponseCode.BUSINESS_ERROR
                )
        
        return get_item
    
    def _create_count_endpoint(self, crud_instance: BaseCRUD, model_class: Type[BaseModel]):
        """创建计数端点（POST方法）"""
        
        async def count_items(request: CountRequest):
            try:
                async with get_database() as session:
                    total = await crud_instance.count(
                        session,
                        filters=request.filters,
                        include_deleted=request.include_deleted
                    )
                    return success_response(
                        data={"count": total},
                        message=ResponseMessage.QUERIED,
                        ret_code=ResponseCode.SUCCESS
                    )
            except Exception as e:
                logger.error(f"Count {model_class.__name__} failed: {e}")
                return error_response(
                    message=f"统计{model_class.__name__}数量失败: {str(e)}",
                    ret_code=ResponseCode.BUSINESS_ERROR
                )
        
        return count_items
    
    def _create_update_endpoint(self, crud_instance: BaseCRUD, model_class: Type[BaseModel], update_model_class):
        """创建更新端点（POST方法）"""
        
        async def update_item(request: UpdateRequest):
            try:
                async with get_database() as session:
                    updated_item = await crud_instance.update_by_id(
                        session,
                        request.id,
                        request.data
                    )
                    return success_response(
                        data=updated_item.to_dict(),
                        message=ResponseMessage.UPDATED,
                        ret_code=ResponseCode.SUCCESS
                    )
            except RecordNotFoundError:
                return error_response(
                    message=f"{model_class.__name__}不存在",
                    ret_code=ResponseCode.NOT_FOUND,
                    http_status=404
                )
            except Exception as e:
                logger.error(f"Update {model_class.__name__} failed: {e}")
                return error_response(
                    message=f"更新{model_class.__name__}失败: {str(e)}",
                    ret_code=ResponseCode.BUSINESS_ERROR
                )
        
        return update_item
    
    def _create_delete_endpoint(self, crud_instance: BaseCRUD, model_class: Type[BaseModel]):
        """创建删除端点（POST方法）"""
        
        async def delete_item(request: DeleteRequest):
            try:
                async with get_database() as session:
                    success = await crud_instance.delete(session, request.id)
                    if success:
                        return None  # 204 No Content
                    else:
                        return error_response(
                            message=f"删除{model_class.__name__}失败",
                            ret_code=ResponseCode.BUSINESS_ERROR
                        )
            except RecordNotFoundError:
                return error_response(
                    message=f"{model_class.__name__}不存在",
                    ret_code=ResponseCode.NOT_FOUND,
                    http_status=404
                )
            except Exception as e:
                logger.error(f"Delete {model_class.__name__} failed: {e}")
                return error_response(
                    message=f"删除{model_class.__name__}失败: {str(e)}",
                    ret_code=ResponseCode.BUSINESS_ERROR
                )
        
        return delete_item
    
    def _create_soft_delete_endpoint(self, crud_instance: BaseCRUD, model_class: Type[BaseModel]):
        """创建软删除端点（POST方法）"""
        
        async def soft_delete_item(request: DeleteRequest):
            try:
                async with get_database() as session:
                    item = await crud_instance.soft_delete(session, request.id)
                    return success_response(
                        data=item.to_dict(),
                        message=ResponseMessage.DELETED,
                        ret_code=ResponseCode.SUCCESS
                    )
            except RecordNotFoundError:
                return error_response(
                    message=f"{model_class.__name__}不存在",
                    ret_code=ResponseCode.NOT_FOUND,
                    http_status=404
                )
            except Exception as e:
                logger.error(f"Soft delete {model_class.__name__} failed: {e}")
                return error_response(
                    message=f"软删除{model_class.__name__}失败: {str(e)}",
                    ret_code=ResponseCode.BUSINESS_ERROR
                )
        
        return soft_delete_item
    
    def _create_restore_endpoint(self, crud_instance: BaseCRUD, model_class: Type[BaseModel]):
        """创建恢复端点（POST方法）"""
        
        async def restore_item(request: RestoreRequest):
            try:
                async with get_database() as session:
                    item = await crud_instance.restore(session, request.id)
                    return success_response(
                        data=item.to_dict(),
                        message="恢复成功",
                        ret_code=ResponseCode.SUCCESS
                    )
            except RecordNotFoundError:
                return error_response(
                    message=f"{model_class.__name__}不存在",
                    ret_code=ResponseCode.NOT_FOUND,
                    http_status=404
                )
            except Exception as e:
                logger.error(f"Restore {model_class.__name__} failed: {e}")
                return error_response(
                    message=f"恢复{model_class.__name__}失败: {str(e)}",
                    ret_code=ResponseCode.BUSINESS_ERROR
                )
        
        return restore_item


def auto_generate_api(
    model_class: Type[BaseModel],
    crud_class: Optional[Type[BaseCRUD]] = None,
    router_prefix: Optional[str] = None,
    tags: Optional[List[str]] = None,
    include_endpoints: Optional[List[str]] = None
) -> APIRouter:
    """
    为模型自动生成 REST API 接口的便捷函数
    
    Args:
        model_class: 模型类
        crud_class: CRUD 类，如果为 None 则自动创建
        router_prefix: 路由前缀，默认为模型名称的小写复数形式
        tags: API 标签
        include_endpoints: 包含的端点列表，默认为所有端点
        
    Returns:
        APIRouter: 生成的路由器
    """
    generator = AutoAPIGenerator()
    return generator.generate_api(
        model_class=model_class,
        crud_class=crud_class,
        router_prefix=router_prefix,
        tags=tags,
        include_endpoints=include_endpoints
    )
