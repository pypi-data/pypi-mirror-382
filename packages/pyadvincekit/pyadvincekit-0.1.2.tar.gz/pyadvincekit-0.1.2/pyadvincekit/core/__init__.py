"""
PyAdvanceKit 核心模块

包含框架的核心功能：
- 配置管理
- 异常处理
- 数据库连接
- 数据库迁移
- FastAPI应用工厂
- 响应格式
- 中间件
"""

from pyadvincekit.core.config import Settings
from pyadvincekit.core.exceptions import PyAdvanceKitException
from pyadvincekit.core.database import (
    DatabaseManager,
    get_database_manager,
    get_database,
    get_db,
    init_database,
    close_database,
    check_database_health,
    reset_database_manager,
    set_database_manager
)

# FastAPI集成模块（阶段三新增）
from pyadvincekit.core.app_factory import create_app, FastAPIAppFactory, app_factory
from pyadvincekit.core.response import (
    success_response,
    error_response,
    paginated_response,
    ResponseCode,
    ResponseMessage,
    BaseResponse,
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse,
)
from pyadvincekit.core.exception_handler import setup_exception_handlers
from pyadvincekit.core.middleware import (
    setup_request_logging_middleware,
    setup_performance_middleware,
    setup_request_id_middleware,
    setup_security_headers_middleware,
    setup_all_middleware,
)

# 定时任务模块
from pyadvincekit.core.scheduler import (
    TaskScheduler,
    TaskInfo,
    TaskStatus,
    TaskType,
    get_scheduler,
    schedule_task,
    schedule_once,
    schedule_interval,
    schedule_cron,
    start_scheduler,
    stop_scheduler,
    get_task_status,
    list_tasks,
    remove_task,
    scheduled_task,
    interval_task,
    cron_task,
)

# 多服务调用模块
from pyadvincekit.core.service_client import (
    ServiceRegistry,
    ServiceClient,
    ServiceEndpoint,
    ServiceCall,
    ServiceStatus,
    CallType,
    get_service_client,
    register_service,
    call_service,
    batch_call_services,
    get_service_stats,
    service_call,
    health_check_service,
    health_check_all_services,
)

from pyadvincekit.core.service_provider import (
    ServiceProvider,
    ServiceHandler,
    ServiceRequest,
    ServiceResponse,
    ServiceMethod,
    get_service_provider,
    register_service_handler,
    handle_service_request,
    service_endpoint,
    get_service_endpoint,
)

# Excel数据库设计生成模块
from pyadvincekit.core.excel_generator import (
    ExcelParser,
    SQLGenerator,
    ORMGenerator,
    PydanticGenerator,
    ExcelCodeGenerator,
    ColumnType,
    ConstraintType,
    TableColumn,
    TableDefinition,
    DatabaseDesign,
    generate_from_excel,
)

# 数据库设计解析器
from pyadvincekit.core.excel_parser import (
    DatabaseDesignParser,
    parse_database_design_excel,
)

# 统一代码生成器
from pyadvincekit.core.code_generator import (
    DatabaseCodeGenerator,
    generate_database_code,
    generate_sql_from_excel,
    generate_orm_from_excel,
    generate_pydantic_from_excel,
)

# 迁移模块为可选导入（需要alembic依赖）
try:
    from pyadvincekit.core.migration import (
        MigrationManager,
        get_migration_manager,
        init_migrations,
        create_migration,
        upgrade_database,
        generate_upgrade_sql,
        downgrade_database,
    )
    _migration_available = True
except ImportError:
    _migration_available = False
    
    # 提供占位符函数
    def _migration_not_available(*args, **kwargs):
        raise ImportError("Migration features require 'alembic' package. Install with: pip install alembic")
    
    MigrationManager = _migration_not_available
    get_migration_manager = _migration_not_available
    init_migrations = _migration_not_available
    create_migration = _migration_not_available
    upgrade_database = _migration_not_available
    generate_upgrade_sql = _migration_not_available
    downgrade_database = _migration_not_available

__all__ = [
    # 配置
    "Settings",
    
    # 异常
    "PyAdvanceKitException",
    
    # 数据库
    "DatabaseManager",
    "get_database_manager", 
    "get_database",
    "get_db",
    "init_database",
    "close_database",
    "check_database_health",
    "reset_database_manager",
    "set_database_manager",
    
    # FastAPI应用工厂
    "create_app",
    "FastAPIAppFactory", 
    "app_factory",
    
    # 响应格式
    "success_response",
    "error_response", 
    "paginated_response",
    "ResponseCode",
    "ResponseMessage",
    "BaseResponse",
    "SuccessResponse",
    "ErrorResponse", 
    "PaginatedResponse",
    
    # 异常处理
    "setup_exception_handlers",
    
    # 中间件
    "setup_request_logging_middleware",
    "setup_performance_middleware",
    "setup_request_id_middleware", 
    "setup_security_headers_middleware",
    "setup_all_middleware",
    
    # 定时任务
    "TaskScheduler",
    "TaskInfo",
    "TaskStatus",
    "TaskType",
    "get_scheduler",
    "schedule_task",
    "schedule_once",
    "schedule_interval",
    "schedule_cron",
    "start_scheduler",
    "stop_scheduler",
    "get_task_status",
    "list_tasks",
    "remove_task",
    "scheduled_task",
    "interval_task",
    "cron_task",
    
    # 多服务调用
    "ServiceRegistry",
    "ServiceClient",
    "ServiceEndpoint",
    "ServiceCall",
    "ServiceStatus",
    "CallType",
    "get_service_client",
    "register_service",
    "call_service",
    "batch_call_services",
    "get_service_stats",
    "service_call",
    "health_check_service",
    "health_check_all_services",
    "ServiceProvider",
    "ServiceHandler",
    "ServiceRequest",
    "ServiceResponse",
    "ServiceMethod",
    "get_service_provider",
    "register_service_handler",
    "handle_service_request",
    "service_endpoint",
    "get_service_endpoint",
    
    # Excel数据库设计生成
    "ExcelParser",
    "SQLGenerator", 
    "ORMGenerator",
    "PydanticGenerator",
    "ExcelCodeGenerator",
    "ColumnType",
    "ConstraintType",
    "TableColumn",
    "TableDefinition",
    "DatabaseDesign",
    "generate_from_excel",
    
    # 数据库设计解析器
    "DatabaseDesignParser",
    "parse_database_design_excel",
    
    # 统一代码生成器
    "DatabaseCodeGenerator",
    "generate_database_code",
    "generate_sql_from_excel",
    "generate_orm_from_excel",
    "generate_pydantic_from_excel",
    
    # 迁移
    "MigrationManager",
    "get_migration_manager",
    "init_migrations",
    "create_migration",
    "upgrade_database",
    "downgrade_database",
]
