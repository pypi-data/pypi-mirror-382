"""
异常处理模块

定义框架的异常类型层次结构，提供统一的异常处理机制。
"""

from typing import Any, Dict, Optional, Union


class PyAdvanceKitException(Exception):
    """PyAdvanceKit 框架基础异常类"""
    
    def __init__(
        self,
        message: str = "An error occurred",
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ) -> None:
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.error_code}: {self.message}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message='{self.message}', "
            f"error_code='{self.error_code}', "
            f"status_code={self.status_code}, "
            f"details={self.details})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于API响应"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "status_code": self.status_code
        }


class ConfigurationError(PyAdvanceKitException):
    """配置错误异常"""
    
    def __init__(
        self,
        message: str = "Configuration error",
        config_key: Optional[str] = None,
        **kwargs
    ) -> None:
        details = kwargs.pop("details", {})
        if config_key:
            details["config_key"] = config_key
        super().__init__(message, details=details, status_code=500, **kwargs)


class DatabaseError(PyAdvanceKitException):
    """数据库操作异常"""
    
    def __init__(
        self,
        message: str = "Database operation failed",
        operation: Optional[str] = None,
        **kwargs
    ) -> None:
        details = kwargs.pop("details", {})
        if operation:
            details["operation"] = operation
        super().__init__(message, details=details, status_code=500, **kwargs)


class ValidationError(PyAdvanceKitException):
    """数据验证异常"""
    
    def __init__(
        self,
        message: str = "Validation failed",
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ) -> None:
        details = kwargs.pop("details", {})
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        super().__init__(message, details=details, status_code=422, **kwargs)


class AuthenticationError(PyAdvanceKitException):
    """身份认证异常"""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        **kwargs
    ) -> None:
        super().__init__(message, status_code=401, **kwargs)


class AuthorizationError(PyAdvanceKitException):
    """权限授权异常"""
    
    def __init__(
        self,
        message: str = "Access denied",
        required_permission: Optional[str] = None,
        **kwargs
    ) -> None:
        details = kwargs.pop("details", {})
        if required_permission:
            details["required_permission"] = required_permission
        super().__init__(message, details=details, status_code=403, **kwargs)


class NotFoundError(PyAdvanceKitException):
    """资源不存在异常"""
    
    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[Union[str, int]] = None,
        **kwargs
    ) -> None:
        details = kwargs.pop("details", {})
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id is not None:
            details["resource_id"] = str(resource_id)
        super().__init__(message, details=details, status_code=404, **kwargs)


class ConflictError(PyAdvanceKitException):
    """资源冲突异常"""
    
    def __init__(
        self,
        message: str = "Resource conflict",
        conflict_field: Optional[str] = None,
        **kwargs
    ) -> None:
        details = kwargs.pop("details", {})
        if conflict_field:
            details["conflict_field"] = conflict_field
        super().__init__(message, details=details, status_code=409, **kwargs)


class RateLimitError(PyAdvanceKitException):
    """请求频率限制异常"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs
    ) -> None:
        details = kwargs.pop("details", {})
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(message, details=details, status_code=429, **kwargs)


class ExternalServiceError(PyAdvanceKitException):
    """外部服务异常"""
    
    def __init__(
        self,
        message: str = "External service error",
        service_name: Optional[str] = None,
        **kwargs
    ) -> None:
        details = kwargs.pop("details", {})
        if service_name:
            details["service_name"] = service_name
        super().__init__(message, details=details, status_code=503, **kwargs)


# 数据库相关异常
class DatabaseConnectionError(DatabaseError):
    """数据库连接异常"""
    
    def __init__(self, message: str = "Database connection failed", **kwargs):
        super().__init__(message, operation="connection", **kwargs)


class RecordNotFoundError(NotFoundError):
    """数据库记录不存在异常"""
    
    def __init__(
        self,
        message: str = "Record not found",
        model: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(
            message, 
            resource_type=model or "record", 
            **kwargs
        )


class RecordAlreadyExistsError(ConflictError):
    """数据库记录已存在异常"""
    
    def __init__(
        self,
        message: str = "Record already exists",
        model: Optional[str] = None,
        **kwargs
    ) -> None:
        details = kwargs.pop("details", {})
        if model:
            details["model"] = model
        super().__init__(message, details=details, **kwargs)


class IntegrityConstraintError(DatabaseError):
    """数据完整性约束异常"""
    
    def __init__(
        self,
        message: str = "Integrity constraint violation",
        constraint: Optional[str] = None,
        **kwargs
    ) -> None:
        details = kwargs.pop("details", {})
        if constraint:
            details["constraint"] = constraint
        super().__init__(message, operation="integrity_check", details=details, **kwargs)


# 业务逻辑异常
class BusinessLogicError(PyAdvanceKitException):
    """业务逻辑异常"""
    
    def __init__(
        self,
        message: str = "Business logic error",
        business_rule: Optional[str] = None,
        **kwargs
    ) -> None:
        details = kwargs.pop("details", {})
        if business_rule:
            details["business_rule"] = business_rule
        super().__init__(message, details=details, status_code=400, **kwargs)


class InsufficientResourceError(BusinessLogicError):
    """资源不足异常"""
    
    def __init__(
        self,
        message: str = "Insufficient resource",
        resource_type: Optional[str] = None,
        required_amount: Optional[Union[int, float]] = None,
        available_amount: Optional[Union[int, float]] = None,
        **kwargs
    ) -> None:
        details = kwargs.pop("details", {})
        if resource_type:
            details["resource_type"] = resource_type
        if required_amount is not None:
            details["required_amount"] = required_amount
        if available_amount is not None:
            details["available_amount"] = available_amount
        super().__init__(message, details=details, **kwargs)


class OperationNotAllowedError(BusinessLogicError):
    """操作不被允许异常"""
    
    def __init__(
        self,
        message: str = "Operation not allowed",
        operation: Optional[str] = None,
        reason: Optional[str] = None,
        **kwargs
    ) -> None:
        details = kwargs.pop("details", {})
        if operation:
            details["operation"] = operation
        if reason:
            details["reason"] = reason
        super().__init__(message, details=details, **kwargs)


# 异常映射字典，用于HTTP状态码映射
EXCEPTION_STATUS_MAP = {
    PyAdvanceKitException: 500,
    ConfigurationError: 500,
    DatabaseError: 500,
    DatabaseConnectionError: 503,
    ValidationError: 422,
    AuthenticationError: 401,
    AuthorizationError: 403,
    NotFoundError: 404,
    RecordNotFoundError: 404,
    ConflictError: 409,
    RecordAlreadyExistsError: 409,
    IntegrityConstraintError: 409,
    RateLimitError: 429,
    ExternalServiceError: 503,
    BusinessLogicError: 400,
    InsufficientResourceError: 400,
    OperationNotAllowedError: 400,
}


def get_exception_status_code(exception: Exception) -> int:
    """获取异常对应的HTTP状态码"""
    if isinstance(exception, PyAdvanceKitException):
        return exception.status_code
    
    # 根据异常类型映射状态码
    for exc_type, status_code in EXCEPTION_STATUS_MAP.items():
        if isinstance(exception, exc_type):
            return status_code
    
    # 默认返回500
    return 500

