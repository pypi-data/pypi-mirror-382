"""
统一响应格式模块

提供标准化的API响应格式和相关工具函数。
新的响应格式包含三层结构：sysHead + appHead + body
"""

from typing import Any, Dict, List, Optional, TypeVar, Generic, Union
from pydantic import BaseModel, Field
from fastapi import status
from fastapi.responses import JSONResponse


# 泛型类型变量
T = TypeVar("T")


class TransactionResult(BaseModel):
    """交易结果"""
    
    retCode: str = Field(description="返回码")
    retMsg: str = Field(description="返回消息")


class SysHead(BaseModel):
    """系统头部信息"""
    
    tranStat: str = Field(description="交易状态", default="true")
    tranRet: List[TransactionResult] = Field(description="交易返回信息", default_factory=list)
    respRecNum: Optional[int] = Field(description="响应记录数", default=None)
    totNum: Optional[int] = Field(description="总记录数", default=None)
    endFlg: Optional[str] = Field(description="结束标志", default=None)


class AppHead(BaseModel):
    """应用头部信息"""
    
    flowIns: Optional[str] = Field(description="流程实例", default=None)
    flowShowData: Optional[str] = Field(description="流程显示数据", default=None)
    showPage: Optional[str] = Field(description="显示页面", default=None)
    flowStat: Optional[str] = Field(description="流程状态", default=None)


class StandardResponse(BaseModel, Generic[T]):
    """标准响应格式"""
    
    sysHead: SysHead = Field(description="系统头部")
    appHead: AppHead = Field(description="应用头部")
    body: T = Field(description="响应数据体")
    
    class Config:
        json_encoders = {
            # 可以在这里添加自定义编码器
        }


# 为了兼容性，保留原有的响应模型（内部使用）
class BaseResponse(BaseModel, Generic[T]):
    """基础响应模型（内部使用）"""
    
    code: int = Field(description="响应状态码")
    message: str = Field(description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")


class SuccessResponse(BaseResponse[T]):
    """成功响应模型（内部使用）"""
    
    code: int = Field(default=0, description="成功状态码")
    message: str = Field(default="success", description="成功消息")


class ErrorResponse(BaseResponse[None]):
    """错误响应模型（内部使用）"""
    
    code: int = Field(description="错误状态码")
    message: str = Field(description="错误消息")
    data: None = Field(default=None, description="错误响应无数据")
    details: Optional[Dict[str, Any]] = Field(default=None, description="错误详情")


class PaginationMeta(BaseModel):
    """分页元信息"""
    
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页大小")
    total: int = Field(description="总记录数")
    total_pages: int = Field(description="总页数")
    has_next: bool = Field(description="是否有下一页")
    has_prev: bool = Field(description="是否有上一页")


class PaginatedData(BaseModel, Generic[T]):
    """分页数据模型"""
    
    items: List[T] = Field(description="数据列表")
    meta: PaginationMeta = Field(description="分页信息")


class PaginatedResponse(SuccessResponse[PaginatedData[T]]):
    """分页响应模型"""
    pass


# 新的响应工具函数
def success_response(
    data: Any = None,
    message: str = "交易成功",
    ret_code: str = "000000",
    total_count: Optional[int] = None,
    response_record_count: Optional[int] = None
) -> Dict[str, Any]:
    """创建成功响应（新格式）"""
    
    # 构建系统头部
    sys_head = SysHead(
        tranStat="true",
        tranRet=[TransactionResult(retCode=ret_code, retMsg=message)],
        respRecNum=response_record_count,
        totNum=total_count,
        endFlg=None
    )
    
    # 构建应用头部（默认为空）
    app_head = AppHead()
    
    # 如果data是列表，直接作为body；否则包装成列表
    if isinstance(data, list):
        body = data
        if response_record_count is None:
            sys_head.respRecNum = len(data)
    elif data is not None:
        body = [data]
        if response_record_count is None:
            sys_head.respRecNum = 1
    else:
        body = []
        if response_record_count is None:
            sys_head.respRecNum = 0
    
    return {
        "sysHead": sys_head.model_dump(),
        "appHead": app_head.model_dump(),
        "body": body
    }


def error_response(
    message: str,
    ret_code: str = "999999",
    details: Optional[Dict[str, Any]] = None,
    http_status: int = status.HTTP_400_BAD_REQUEST
) -> JSONResponse:
    """创建错误响应（新格式）"""
    
    # 构建系统头部
    sys_head = SysHead(
        tranStat="false",
        tranRet=[TransactionResult(retCode=ret_code, retMsg=message)],
        respRecNum=0,
        totNum=0,
        endFlg=None
    )
    
    # 构建应用头部（默认为空）
    app_head = AppHead()
    
    # 错误响应的body为空列表，但可以包含详情
    body = []
    if details:
        body = [{"error_details": details}]
        sys_head.respRecNum = 1
    
    response_data = {
        "sysHead": sys_head.model_dump(),
        "appHead": app_head.model_dump(),
        "body": body
    }
    
    return JSONResponse(
        status_code=http_status,
        content=response_data
    )


def paginated_response(
    items: List[Any],
    page: int,
    page_size: int,
    total: int,
    message: str = "查询成功",
    ret_code: str = "000000"
) -> Dict[str, Any]:
    """创建分页响应（新格式）"""
    
    # 构建分页元信息并添加到每个项目中（或者作为单独的元信息项）
    total_pages = (total + page_size - 1) // page_size
    
    # 分页元信息可以添加到body的第一个元素，或者作为单独的信息
    pagination_meta = {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }
    
    # 将分页信息添加到appHead中
    app_head = AppHead(
        flowShowData=f"第{page}页，共{total_pages}页",
        showPage=str(page)
    )
    
    return {
        "sysHead": SysHead(
            tranStat="true",
            tranRet=[TransactionResult(retCode=ret_code, retMsg=message)],
            respRecNum=len(items),
            totNum=total,
            endFlg="true" if page >= total_pages else "false"
        ).model_dump(),
        "appHead": app_head.model_dump(),
        "body": items
    }


# 兼容性函数（内部使用旧格式）
def legacy_success_response(
    data: Any = None,
    message: str = "success",
    code: int = 0
) -> Dict[str, Any]:
    """创建成功响应（旧格式，内部使用）"""
    return {
        "code": code,
        "message": message,
        "data": data
    }


def legacy_error_response(
    message: str,
    code: int = 1,
    details: Optional[Dict[str, Any]] = None,
    http_status: int = status.HTTP_400_BAD_REQUEST
) -> JSONResponse:
    """创建错误响应（旧格式，内部使用）"""
    response_data = {
        "code": code,
        "message": message,
        "data": None
    }
    
    if details:
        response_data["details"] = details
    
    return JSONResponse(
        status_code=http_status,
        content=response_data
    )


# 新的响应码常量（6位数字格式）
class ResponseCode:
    """响应状态码常量（新格式）"""
    
    # 成功状态码
    SUCCESS = "000000"
    
    # 客户端错误 (4xxxxx)
    BAD_REQUEST = "400001"
    UNAUTHORIZED = "401001"
    FORBIDDEN = "403001"
    NOT_FOUND = "404001"
    METHOD_NOT_ALLOWED = "405001"
    CONFLICT = "409001"
    VALIDATION_ERROR = "422001"
    TOO_MANY_REQUESTS = "429001"
    
    # 服务器错误 (5xxxxx)
    INTERNAL_SERVER_ERROR = "500001"
    NOT_IMPLEMENTED = "501001"
    BAD_GATEWAY = "502001"
    SERVICE_UNAVAILABLE = "503001"
    GATEWAY_TIMEOUT = "504001"
    
    # 业务错误码 (9xxxxx)
    BUSINESS_ERROR = "900001"
    DATA_NOT_FOUND = "900002"
    DATA_ALREADY_EXISTS = "900003"
    INVALID_OPERATION = "900004"
    INSUFFICIENT_PERMISSIONS = "900005"
    
    # 系统通用错误
    SYSTEM_ERROR = "999999"


class ResponseMessage:
    """响应消息常量（新格式）"""
    
    # 通用消息
    SUCCESS = "交易成功"
    FAILURE = "交易失败"
    
    # 数据操作消息
    CREATED = "创建成功"
    UPDATED = "更新成功"
    DELETED = "删除成功"
    QUERIED = "查询成功"
    
    # 错误消息
    BAD_REQUEST = "请求参数错误"
    UNAUTHORIZED = "未授权访问"
    FORBIDDEN = "禁止访问"
    NOT_FOUND = "资源不存在"
    METHOD_NOT_ALLOWED = "不支持的请求方法"
    CONFLICT = "资源冲突"
    VALIDATION_ERROR = "数据验证失败"
    TOO_MANY_REQUESTS = "请求过于频繁"
    INTERNAL_SERVER_ERROR = "服务器内部错误"
    SERVICE_UNAVAILABLE = "服务暂不可用"
    
    # 业务错误消息
    DATA_NOT_FOUND = "数据不存在"
    DATA_ALREADY_EXISTS = "数据已存在"
    INVALID_OPERATION = "无效操作"
    INSUFFICIENT_PERMISSIONS = "权限不足"
    
    # 系统错误消息
    SYSTEM_ERROR = "系统异常"


# 兼容性常量（内部使用）
class LegacyResponseCode:
    """响应状态码常量（旧格式，内部使用）"""
    
    SUCCESS = 0
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    BUSINESS_ERROR = 1000


# FastAPI响应装饰器（新格式）
def api_response(
    success_message: str = ResponseMessage.SUCCESS,
    success_code: str = ResponseCode.SUCCESS
):
    """API响应装饰器（新格式）"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                
                # 如果返回值已经是新格式（包含sysHead字段），直接返回
                if isinstance(result, dict) and "sysHead" in result:
                    return result
                
                # 否则包装成标准响应格式
                return success_response(result, success_message, success_code)
                
            except Exception as e:
                # 这里会被全局异常处理器捕获
                raise e
        
        return wrapper
    return decorator


# 兼容性装饰器（内部使用）
def legacy_api_response(
    success_message: str = "success",
    success_code: int = 0
):
    """API响应装饰器（旧格式，内部使用）"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                
                if isinstance(result, dict) and "code" in result:
                    return result
                
                return legacy_success_response(result, success_message, success_code)
                
            except Exception as e:
                raise e
        
        return wrapper
    return decorator


# 响应类型定义
ResponseType = Union[
    Dict[str, Any],      # 标准响应格式（新格式）
    JSONResponse,        # FastAPI JSON响应
    StandardResponse,    # Pydantic响应模型（新格式）
]

# 兼容性响应类型
LegacyResponseType = Union[
    Dict[str, Any],  # 标准响应格式（旧格式）
    JSONResponse,    # FastAPI JSON响应
    BaseResponse,    # Pydantic响应模型（旧格式）
]



