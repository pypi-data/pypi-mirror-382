"""
全局异常处理器

为FastAPI应用提供统一的异常处理机制。
"""

from typing import Union
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, OperationalError

from pyadvincekit.core.config import get_settings
from pyadvincekit.core.exceptions import (
    PyAdvanceKitException,
    DatabaseError,
    ValidationError as CustomValidationError,
    NotFoundError,
    ConflictError,
    AuthenticationError,
    AuthorizationError,
    BusinessLogicError,
    RecordNotFoundError,
    RecordAlreadyExistsError,
)
from pyadvincekit.core.response import (
    error_response,
    ResponseCode,
    ResponseMessage,
)

from pyadvincekit.logging import get_logger

logger = get_logger(__name__)


class ExceptionHandler:
    """异常处理器类"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.settings = get_settings()
        self._register_handlers()
    
    def _register_handlers(self):
        """注册异常处理器"""
        
        # PyAdvanceKit自定义异常
        @self.app.exception_handler(PyAdvanceKitException)
        async def pyadvincekit_exception_handler(
            request: Request, 
            exc: PyAdvanceKitException
        ) -> JSONResponse:
            return await self._handle_pyadvincekit_exception(request, exc)
        
        # HTTP异常
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(
            request: Request, 
            exc: HTTPException
        ) -> JSONResponse:
            return await self._handle_http_exception(request, exc)
        
        # 请求验证异常
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(
            request: Request, 
            exc: RequestValidationError
        ) -> JSONResponse:
            return await self._handle_validation_exception(request, exc)
        
        # Pydantic验证异常
        @self.app.exception_handler(ValidationError)
        async def pydantic_validation_exception_handler(
            request: Request, 
            exc: ValidationError
        ) -> JSONResponse:
            return await self._handle_pydantic_validation_exception(request, exc)
        
        # 数据库异常
        @self.app.exception_handler(IntegrityError)
        async def integrity_error_handler(
            request: Request, 
            exc: IntegrityError
        ) -> JSONResponse:
            return await self._handle_integrity_error(request, exc)
        
        @self.app.exception_handler(OperationalError)
        async def operational_error_handler(
            request: Request, 
            exc: OperationalError
        ) -> JSONResponse:
            return await self._handle_operational_error(request, exc)
        
        # 通用异常
        @self.app.exception_handler(Exception)
        async def general_exception_handler(
            request: Request, 
            exc: Exception
        ) -> JSONResponse:
            return await self._handle_general_exception(request, exc)
    
    async def _handle_pyadvincekit_exception(
        self, 
        request: Request, 
        exc: PyAdvanceKitException
    ) -> JSONResponse:
        """处理PyAdvanceKit自定义异常"""
        
        # 记录异常日志
        logger.warning(
            f"PyAdvanceKit异常: {exc.__class__.__name__}: {exc.message}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "path": request.url.path,
                "method": request.method,
                "exception_details": exc.details
            }
        )
        
        # 根据异常类型确定HTTP状态码
        http_status = self._get_http_status_for_exception(exc)
        
        # 构建错误响应
        details = exc.details if self.settings.is_development() else None
        
        return error_response(
            message=exc.message,
            ret_code=str(exc.status_code),
            details=details,
            http_status=http_status
        )
    
    async def _handle_http_exception(
        self, 
        request: Request, 
        exc: HTTPException
    ) -> JSONResponse:
        """处理HTTP异常"""
        
        logger.warning(
            f"HTTP异常: {exc.status_code}: {exc.detail}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "path": request.url.path,
                "method": request.method
            }
        )
        
        # 映射常见HTTP状态码到业务消息
        message_map = {
            404: ResponseMessage.NOT_FOUND,
            401: ResponseMessage.UNAUTHORIZED,
            403: ResponseMessage.FORBIDDEN,
            405: ResponseMessage.METHOD_NOT_ALLOWED,
            429: ResponseMessage.TOO_MANY_REQUESTS,
        }
        
        message = message_map.get(exc.status_code, str(exc.detail))
        
        return error_response(
            message=message,
            ret_code=str(exc.status_code),  # 🔥 转换为字符串
            http_status=exc.status_code
        )
    
    async def _handle_validation_exception(
        self, 
        request: Request, 
        exc: RequestValidationError
    ) -> JSONResponse:
        """处理请求验证异常"""
        
        logger.warning(
            f"请求验证异常: {exc}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "path": request.url.path,
                "method": request.method,
                "errors": exc.errors()
            }
        )
        
        # 格式化验证错误信息
        formatted_errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            formatted_errors.append(f"{field}: {message}")
        
        details = {
            "validation_errors": exc.errors()
        } if self.settings.is_development() else None
        
        return error_response(
            message=f"数据验证失败: {'; '.join(formatted_errors)}",
            ret_code=ResponseCode.VALIDATION_ERROR,
            details=details,
            http_status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    async def _handle_pydantic_validation_exception(
        self, 
        request: Request, 
        exc: ValidationError
    ) -> JSONResponse:
        """处理Pydantic验证异常"""
        
        logger.warning(
            f"Pydantic验证异常: {exc}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "path": request.url.path,
                "method": request.method
            }
        )
        
        return error_response(
            message=ResponseMessage.VALIDATION_ERROR,
            ret_code=ResponseCode.VALIDATION_ERROR,
            details={"errors": exc.errors()} if self.settings.is_development() else None,
            http_status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    async def _handle_integrity_error(
        self, 
        request: Request, 
        exc: IntegrityError
    ) -> JSONResponse:
        """处理数据库完整性约束异常"""
        
        logger.error(
            f"数据库完整性错误: {exc}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "path": request.url.path,
                "method": request.method
            }
        )
        
        # 检查是否为唯一约束冲突
        if "UNIQUE constraint failed" in str(exc) or "duplicate key" in str(exc):
            message = ResponseMessage.DATA_ALREADY_EXISTS
            code = ResponseCode.CONFLICT
            http_status = status.HTTP_409_CONFLICT
        else:
            message = "数据完整性约束违反"
            code = ResponseCode.BAD_REQUEST
            http_status = status.HTTP_400_BAD_REQUEST
        
        details = {"database_error": str(exc)} if self.settings.is_development() else None
        
        return error_response(
            message=message,
            ret_code=code,
            details=details,
            http_status=http_status
        )
    
    async def _handle_operational_error(
        self, 
        request: Request, 
        exc: OperationalError
    ) -> JSONResponse:
        """处理数据库操作异常"""
        
        logger.error(
            f"数据库操作错误: {exc}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "path": request.url.path,
                "method": request.method
            }
        )
        
        return error_response(
            message="数据库操作失败",
            ret_code=ResponseCode.INTERNAL_SERVER_ERROR,
            details={"database_error": str(exc)} if self.settings.is_development() else None,
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    async def _handle_general_exception(
        self, 
        request: Request, 
        exc: Exception
    ) -> JSONResponse:
        """处理通用异常"""
        
        logger.error(
            f"未处理的异常: {exc.__class__.__name__}: {exc}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "path": request.url.path,
                "method": request.method
            },
            exc_info=True
        )
        
        # 生产环境隐藏详细错误信息
        if self.settings.is_production():
            message = ResponseMessage.INTERNAL_SERVER_ERROR
            details = None
        else:
            message = f"{exc.__class__.__name__}: {str(exc)}"
            details = {
                "exception_type": exc.__class__.__name__,
                "exception_message": str(exc)
            }
        
        return error_response(
            message=message,
            ret_code=ResponseCode.INTERNAL_SERVER_ERROR,
            details=details,
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    def _get_http_status_for_exception(self, exc: PyAdvanceKitException) -> int:
        """根据异常类型获取HTTP状态码"""
        
        status_map = {
            CustomValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
            NotFoundError: status.HTTP_404_NOT_FOUND,
            RecordNotFoundError: status.HTTP_404_NOT_FOUND,
            ConflictError: status.HTTP_409_CONFLICT,
            RecordAlreadyExistsError: status.HTTP_409_CONFLICT,
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            BusinessLogicError: status.HTTP_400_BAD_REQUEST,
            DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
        
        return status_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


def setup_exception_handlers(app: FastAPI) -> ExceptionHandler:
    """设置异常处理器"""
    return ExceptionHandler(app)
