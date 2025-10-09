"""
通用请求和响应Schema

提供标准化的请求参数模型，用于POST接口的参数传递。
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class GetByIdRequest(BaseModel):
    """根据ID获取单个记录的请求"""
    
    id: str = Field(description="记录ID")


class QueryRequest(BaseModel):
    """查询列表的请求"""
    
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=10, ge=1, le=100, description="每页大小")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="过滤条件")
    order_by: Optional[str] = Field(default=None, description="排序字段")
    order_desc: bool = Field(default=False, description="是否降序排列")
    include_deleted: bool = Field(default=False, description="是否包含已删除记录")


class DeleteRequest(BaseModel):
    """删除记录的请求"""
    
    id: str = Field(description="要删除的记录ID")


class BatchDeleteRequest(BaseModel):
    """批量删除记录的请求"""
    
    ids: List[str] = Field(description="要删除的记录ID列表", min_items=1)


class UpdateRequest(BaseModel):
    """更新记录的请求"""
    
    id: str = Field(description="要更新的记录ID")
    data: Dict[str, Any] = Field(description="更新数据")


class CountRequest(BaseModel):
    """统计记录数量的请求"""
    
    filters: Optional[Dict[str, Any]] = Field(default=None, description="过滤条件")
    include_deleted: bool = Field(default=False, description="是否包含已删除记录")


class ExistsRequest(BaseModel):
    """检查记录是否存在的请求"""
    
    id: str = Field(description="记录ID")


class RestoreRequest(BaseModel):
    """恢复软删除记录的请求"""
    
    id: str = Field(description="要恢复的记录ID")


class BulkCreateRequest(BaseModel):
    """批量创建记录的请求"""
    
    items: List[Dict[str, Any]] = Field(description="要创建的记录列表", min_items=1)


# 通用响应Schema（用于类型提示）
class IdResponse(BaseModel):
    """ID响应"""
    
    id: str = Field(description="记录ID")


class CountResponse(BaseModel):
    """计数响应"""
    
    count: int = Field(description="记录数量")


class ExistsResponse(BaseModel):
    """存在性检查响应"""
    
    exists: bool = Field(description="是否存在")


class BulkOperationResponse(BaseModel):
    """批量操作响应"""
    
    success_count: int = Field(description="成功数量")
    failed_count: int = Field(default=0, description="失败数量")
    errors: Optional[List[Dict[str, Any]]] = Field(default=None, description="错误详情")


# 分页相关Schema
class PaginationInfo(BaseModel):
    """分页信息"""
    
    page: int = Field(description="当前页码")
    size: int = Field(description="每页大小")
    total: int = Field(description="总记录数")
    total_pages: int = Field(description="总页数")
    has_next: bool = Field(description="是否有下一页")
    has_prev: bool = Field(description="是否有上一页")


class PaginatedListResponse(BaseModel):
    """分页列表响应"""
    
    items: List[Dict[str, Any]] = Field(description="数据列表")
    pagination: PaginationInfo = Field(description="分页信息")


# 业务操作相关Schema
class BusinessActionRequest(BaseModel):
    """业务操作请求基类"""
    
    id: str = Field(description="目标记录ID")
    action: str = Field(description="操作类型")
    params: Optional[Dict[str, Any]] = Field(default=None, description="操作参数")


class BatchBusinessActionRequest(BaseModel):
    """批量业务操作请求"""
    
    ids: List[str] = Field(description="目标记录ID列表", min_items=1)
    action: str = Field(description="操作类型")
    params: Optional[Dict[str, Any]] = Field(default=None, description="操作参数")


# 搜索相关Schema
class SearchRequest(BaseModel):
    """搜索请求"""
    
    keyword: str = Field(description="搜索关键词")
    fields: Optional[List[str]] = Field(default=None, description="搜索字段列表")
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=10, ge=1, le=100, description="每页大小")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="额外过滤条件")


# 导入导出相关Schema
class ExportRequest(BaseModel):
    """导出请求"""
    
    format: str = Field(default="excel", description="导出格式")
    fields: Optional[List[str]] = Field(default=None, description="导出字段列表")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="过滤条件")


class ImportRequest(BaseModel):
    """导入请求"""
    
    file_path: str = Field(description="文件路径")
    format: str = Field(default="excel", description="文件格式")
    mapping: Optional[Dict[str, str]] = Field(default=None, description="字段映射")
    validate_only: bool = Field(default=False, description="仅验证不导入")









