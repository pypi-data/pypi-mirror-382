"""
PyAdvanceKit - 高内聚、易扩展、符合团队规范的Python Web开发基础框架

一个基于 FastAPI 和 SQLAlchemy 的现代化 Python Web 开发框架。
"""

__version__ = "0.1.0"
__author__ = "PyAdvanceKit Team"
__email__ = "team@pyadvincekit.com"
__license__ = "MIT"
__url__ = "https://github.com/pyadvincekit/pyadvincekit"

# 🔥 优先修复控制台编码问题（必须在其他导入之前）
import sys
import os

def _init_encoding():
    """初始化编码设置"""
    if sys.platform == 'win32':
        # 设置环境变量
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # 重新配置标准输出流
        try:
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
            if hasattr(sys.stderr, 'reconfigure'):  
                sys.stderr.reconfigure(encoding='utf-8')
        except (AttributeError, ValueError):
            pass

# 立即执行编码初始化
_init_encoding()

# 核心导入
from pyadvincekit.core.config import Settings
from pyadvincekit.core.exceptions import PyAdvanceKitException

# 数据库相关导入（阶段二完成）
from pyadvincekit.core.database import (
    get_database, get_db, init_database, 
    # 事务管理
    begin_transaction, commit_transaction, rollback_transaction, 
    close_session, get_transaction
)
from pyadvincekit.models.base import (
    BaseModel, SoftDeleteModel,
    # 字段创建函数
    create_required_string_column, create_optional_string_column, create_text_column,
    create_integer_column, create_boolean_column, create_datetime_column,
    create_decimal_column, create_json_column, create_uuid_column,
    create_float_column, create_bigint_column, create_enum_column,
    create_date_column, create_time_column, create_binary_column,
    create_email_column, create_phone_column, create_url_column,
    create_status_column, create_sort_order_column, create_foreign_key_column,
    create_version_column
)
from pyadvincekit.crud.base import BaseCRUD, CRUDBase

# FastAPI集成导入（阶段三完成）
from pyadvincekit.core.app_factory import create_app, FastAPIAppFactory, FastAPIWithAutoAPI
from pyadvincekit.core.response import (
    success_response, error_response, paginated_response,
    ResponseCode, ResponseMessage, StandardResponse, SysHead, AppHead, TransactionResult,
    # 兼容性导入
    legacy_success_response, legacy_error_response, LegacyResponseCode
)
from pyadvincekit.core.middleware import setup_all_middleware
from pyadvincekit.core.auto_api import auto_generate_api, AutoAPIGenerator
from pyadvincekit.schemas import (
    GetByIdRequest, QueryRequest, DeleteRequest, UpdateRequest, CountRequest
)
from pyadvincekit.decorators import transactional, transactional_method

# 功能完善层导入（阶段四完成）
from pyadvincekit.logging import (
    setup_logging, get_logger,
    # 第二阶段新增：跟踪功能
    TraceContext, TraceManager, TraceMiddleware,
    trace_function, trace_method,
    get_current_trace_id, get_current_span_id, get_current_context,
    start_trace, create_child_span
)

# 定时任务功能（第二阶段新增）
from pyadvincekit.core.scheduler import (
    TaskScheduler, TaskInfo, TaskStatus, TaskType,
    get_scheduler, schedule_task, schedule_once, schedule_interval, schedule_cron,
    start_scheduler, stop_scheduler, get_task_status, list_tasks, remove_task,
    scheduled_task, interval_task, cron_task
)

# 多服务调用功能（第二阶段新增）
from pyadvincekit.core.service_client import (
    ServiceRegistry, ServiceClient, ServiceEndpoint, ServiceCall, ServiceStatus, CallType,
    get_service_client, register_service, call_service, batch_call_services,
    get_service_stats, service_call, health_check_service, health_check_all_services
)

from pyadvincekit.core.service_provider import (
    ServiceProvider, ServiceHandler, ServiceRequest, ServiceResponse, ServiceMethod,
    get_service_provider, register_service_handler, handle_service_request,
    service_endpoint, get_service_endpoint
)

# Excel数据库设计生成功能（第二阶段新增）
from pyadvincekit.core.excel_generator import (
    ExcelParser, SQLGenerator, ORMGenerator, PydanticGenerator, ExcelCodeGenerator,
    ColumnType, ConstraintType, TableColumn, TableDefinition, DatabaseDesign,
    TableIndex, ColumnConstraint, generate_from_excel
)

# 数据库设计解析器（第二阶段新增）
from pyadvincekit.core.excel_parser import (
    DatabaseDesignParser, parse_database_design_excel
)

# 统一代码生成器（第二阶段新增）
from pyadvincekit.core.code_generator import (
    DatabaseCodeGenerator, generate_database_code,
    generate_sql_from_excel, generate_orm_from_excel, generate_pydantic_from_excel
)

# 数据库逆向生成器（数据库逆向功能）
from pyadvincekit.core.database_generator import (
    generate_from_database, generate_models_from_database, 
    generate_schemas_from_database, generate_all_from_database
)
from pyadvincekit.core.database_extractor import (
    DatabaseMetadataExtractor, DatabaseTypeMapper
)
from pyadvincekit.auth import create_access_token, verify_token, JWTAuth
from pyadvincekit.utils import (
    generate_secret_key, hash_password, encrypt_data,
    validate_email, validate_phone, create_validator,
    now, utc_now, format_duration,
    # 第二阶段新增工具类
    HTTPClient, HTTPUtils, APIClient, create_http_client, create_api_client,
    Money, MoneyUtils, Currency, RoundingMode, money, cny, usd
)

# 配置管理功能
# from pyadvincekit.core.config_manager import (
#     ConfigManager, setup_from_env_file, create_app_from_env,
#     get_global_config_manager, setup_global_config
# )

# 迁移功能为可选导入
try:
    from pyadvincekit.core.migration import init_migrations, create_migration, upgrade_database, generate_upgrade_sql
    _migration_available = True
except ImportError:
    _migration_available = False
    
    def _migration_not_available(*args, **kwargs):
        raise ImportError("Migration features require 'alembic' package. Install with: pip install alembic")
    
    init_migrations = _migration_not_available
    create_migration = _migration_not_available 
    upgrade_database = _migration_not_available
    generate_upgrade_sql = _migration_not_available

__all__ = [
    # 版本信息
    "__version__",
    "__author__", 
    "__email__",
    "__license__",
    "__url__",
    
    # 核心组件
    "Settings",
    "PyAdvanceKitException",
    
    # 数据库组件（阶段二完成）
    "get_database",
    "get_db", 
    "init_database",
    # 事务管理
    "begin_transaction",
    "commit_transaction", 
    "rollback_transaction",
    "close_session",
    "get_transaction",
    "BaseModel",
    "SoftDeleteModel",
    "BaseCRUD",
    "CRUDBase",
    
    # 字段创建函数
    "create_required_string_column",
    "create_optional_string_column", 
    "create_text_column",
    "create_integer_column",
    "create_boolean_column",
    "create_datetime_column",
    "create_decimal_column",
    "create_json_column",
    "create_uuid_column",
    "create_float_column",
    "create_bigint_column", 
    "create_enum_column",
    "create_date_column",
    "create_time_column",
    "create_binary_column",
    "create_email_column",
    "create_phone_column",
    "create_url_column",
    "create_status_column",
    "create_sort_order_column",
    "create_foreign_key_column",
    "create_version_column",
    
    # FastAPI集成（阶段三完成）
    "create_app",
    "FastAPIAppFactory",
    "FastAPIWithAutoAPI",
    "success_response",
    "error_response", 
    "paginated_response",
    "ResponseCode",
    "ResponseMessage",
    "StandardResponse",
    "SysHead",
    "AppHead", 
    "TransactionResult",
    # 兼容性导出
    "legacy_success_response",
    "legacy_error_response",
    "LegacyResponseCode",
    "setup_all_middleware",
    "auto_generate_api",
    "AutoAPIGenerator",
    # 通用Schema
    "GetByIdRequest",
    "QueryRequest",
    "DeleteRequest",
    "UpdateRequest", 
    "CountRequest",
    # 事务装饰器
    "transactional",
    "transactional_method",
    
    # 功能完善层（阶段四完成）
    "setup_logging",
    "get_logger",
    "create_access_token",
    "verify_token",
    "JWTAuth",
    
    # 第二阶段新增：跟踪功能
    "TraceContext", "TraceManager", "TraceMiddleware",
    "trace_function", "trace_method",
    "get_current_trace_id", "get_current_span_id", "get_current_context",
    "start_trace", "create_child_span",
    "generate_secret_key",
    "hash_password",
    "encrypt_data",
    "validate_email",
    "validate_phone",
    "create_validator",
    "now",
    "utc_now",
    "format_duration",
    
    # 第二阶段新增工具类
    "HTTPClient", "HTTPUtils", "APIClient", "create_http_client", "create_api_client",
    "Money", "MoneyUtils", "Currency", "RoundingMode", "money", "cny", "usd",
    
    # 定时任务功能（第二阶段新增）
    "TaskScheduler", "TaskInfo", "TaskStatus", "TaskType",
    "get_scheduler", "schedule_task", "schedule_once", "schedule_interval", "schedule_cron",
    "start_scheduler", "stop_scheduler", "get_task_status", "list_tasks", "remove_task",
    "scheduled_task", "interval_task", "cron_task",
    
    # 多服务调用功能（第二阶段新增）
    "ServiceRegistry", "ServiceClient", "ServiceEndpoint", "ServiceCall", "ServiceStatus", "CallType",
    "get_service_client", "register_service", "call_service", "batch_call_services",
    "get_service_stats", "service_call", "health_check_service", "health_check_all_services",
    "ServiceProvider", "ServiceHandler", "ServiceRequest", "ServiceResponse", "ServiceMethod",
    "get_service_provider", "register_service_handler", "handle_service_request",
    "service_endpoint", "get_service_endpoint",
    
    # Excel数据库设计生成功能（第二阶段新增）
    "ExcelParser", "SQLGenerator", "ORMGenerator", "PydanticGenerator", "ExcelCodeGenerator",
    "ColumnType", "ConstraintType", "TableColumn", "TableDefinition", "DatabaseDesign",
    "TableIndex", "ColumnConstraint", "generate_from_excel",
    
    # 数据库设计解析器（第二阶段新增）
    "DatabaseDesignParser", "parse_database_design_excel",
    
    # 统一代码生成器（第二阶段新增）
    "DatabaseCodeGenerator", "generate_database_code",
    "generate_sql_from_excel", "generate_orm_from_excel", "generate_pydantic_from_excel",
    
    # 数据库逆向生成器（数据库逆向功能）
    "generate_from_database", "generate_models_from_database", 
    "generate_schemas_from_database", "generate_all_from_database",
    "DatabaseMetadataExtractor", "DatabaseTypeMapper",
    
    # 数据库迁移
    "init_migrations",
    "create_migration",
    "upgrade_database",
    "generate_upgrade_sql",
]

# 包级别的配置
import logging

# 设置默认日志级别
logging.getLogger(__name__).addHandler(logging.NullHandler())

# 版本检查
import sys

if sys.version_info < (3, 8):
    raise RuntimeError("PyAdvanceKit requires Python 3.8 or higher")
