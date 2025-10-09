"""
PyAdvanceKit Schemas

提供通用的请求和响应Schema定义。
"""

from pyadvincekit.schemas.common import (
    # 请求Schema
    GetByIdRequest,
    QueryRequest,
    DeleteRequest,
    BatchDeleteRequest,
    UpdateRequest,
    CountRequest,
    ExistsRequest,
    RestoreRequest,
    BulkCreateRequest,
    BusinessActionRequest,
    BatchBusinessActionRequest,
    SearchRequest,
    ExportRequest,
    ImportRequest,
    
    # 响应Schema
    IdResponse,
    CountResponse,
    ExistsResponse,
    BulkOperationResponse,
    PaginationInfo,
    PaginatedListResponse,
)

__all__ = [
    # 请求Schema
    "GetByIdRequest",
    "QueryRequest", 
    "DeleteRequest",
    "BatchDeleteRequest",
    "UpdateRequest",
    "CountRequest",
    "ExistsRequest",
    "RestoreRequest",
    "BulkCreateRequest",
    "BusinessActionRequest",
    "BatchBusinessActionRequest",
    "SearchRequest",
    "ExportRequest",
    "ImportRequest",
    
    # 响应Schema
    "IdResponse",
    "CountResponse",
    "ExistsResponse", 
    "BulkOperationResponse",
    "PaginationInfo",
    "PaginatedListResponse",
]