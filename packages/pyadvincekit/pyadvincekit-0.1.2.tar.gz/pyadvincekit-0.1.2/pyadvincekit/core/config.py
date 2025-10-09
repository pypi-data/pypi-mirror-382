"""
配置管理模块

提供多环境配置支持，基于 Pydantic Settings 实现类型安全的配置管理。
支持从环境变量、配置文件等多种来源加载配置。
"""

import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """环境类型枚举"""
    DEVELOPMENT = "development"
    TESTING = "testing" 
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """日志级别枚举"""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class DatabaseConfig(BaseSettings):
    """数据库配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="PYADVINCEKIT_DATABASE_",
        case_sensitive=False,
        extra="ignore"
    )
    # model_config = SettingsConfigDict(
    #     env_prefix="PYADVINCEKIT_DATABASE__",
    #     case_sensitive=False,
    #     extra="ignore"
    # )
    
    # 数据库连接URL
    url: str = Field(
        default="sqlite:///./app.db",
        description="数据库连接URL"
    )
    
    # 连接池配置
    pool_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="连接池大小"
    )
    
    max_overflow: int = Field(
        default=20,
        ge=0,
        le=100,
        description="连接池最大溢出连接数"
    )
    
    pool_recycle: int = Field(
        default=3600,
        ge=60,
        description="连接回收时间（秒）"
    )
    
    pool_pre_ping: bool = Field(
        default=True,
        description="连接前是否ping检查"
    )
    
    # 查询配置
    echo_sql: bool = Field(
        default=False,
        description="是否输出SQL查询日志"
    )
    
    # 迁移配置
    alembic_ini_path: str = Field(
        default="alembic.ini",
        description="Alembic配置文件路径"
    )

    @validator("url")
    def validate_database_url(cls, v: str) -> str:
        """验证数据库URL格式"""
        if not v:
            raise ValueError("数据库URL不能为空")
        
        # 检查是否为支持的数据库类型
        supported_schemes = [
            "sqlite", "sqlite+aiosqlite",
            "postgresql", "postgresql+asyncpg", "postgresql+psycopg2",
            "mysql", "mysql+aiomysql", "mysql+pymysql"
        ]
        
        scheme = v.split("://")[0] if "://" in v else ""
        if scheme and not any(v.startswith(s) for s in supported_schemes):
            raise ValueError(f"不支持的数据库类型: {scheme}")
        
        return v


class LoggingConfig(BaseSettings):
    """日志配置"""
    
    model_config = SettingsConfigDict(
        env_prefix="PYADVINCEKIT_LOG_",
        case_sensitive=False,
        extra="ignore"
    )
    
    # 基础日志配置
    level: LogLevel = Field(
        default=LogLevel.INFO,
        description="日志级别"
    )
    
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    
    # 文件日志配置
    log_file_enabled: bool = Field(
        default=True,
        description="是否启用文件日志"
    )
    
    log_file_path: str = Field(
        default="logs/app.log",
        description="日志文件路径"
    )
    
    log_file_max_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        ge=1024,
        description="日志文件最大大小（字节）"
    )
    
    log_file_backup_count: int = Field(
        default=5,
        ge=1,
        description="日志文件备份数量"
    )
    
    # 结构化日志配置
    structured_logging: bool = Field(
        default=True,
        description="是否启用结构化日志"
    )
    
    # 请求日志配置
    log_requests: bool = Field(
        default=True,
        description="是否记录请求日志"
    )
    
    log_request_body: bool = Field(
        default=False,
        description="是否记录请求体（敏感信息注意）"
    )


class SecurityConfig(BaseSettings):
    """安全配置"""
    
    model_config = SettingsConfigDict(
        env_prefix="PYADVINCEKIT_JWT_",
        case_sensitive=False,
        extra="ignore"
    )
    
    # JWT配置
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        min_length=32,
        description="JWT密钥"
    )
    
    access_token_expire_minutes: int = Field(
        default=30,
        ge=1,
        description="访问令牌过期时间（分钟）"
    )
    
    refresh_token_expire_days: int = Field(
        default=7,
        ge=1,
        description="刷新令牌过期时间（天）"
    )
    
    # CORS配置
    allow_origins: List[str] = Field(
        default=["*"],
        description="允许的跨域来源"
    )
    
    allow_methods: List[str] = Field(
        default=["*"],
        description="允许的HTTP方法"
    )
    
    allow_headers: List[str] = Field(
        default=["*"],
        description="允许的HTTP头"
    )
    
    allow_credentials: bool = Field(
        default=True,
        description="是否允许携带凭证"
    )


class Settings(BaseSettings):
    """应用主配置类"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="PYADVINCEKIT_",
        case_sensitive=False,
        extra="ignore"
    )
    
    # 应用基础配置
    app_name: str = Field(
        default="PyAdvanceKit App",
        description="应用名称"
    )
    
    app_version: str = Field(
        default="0.1.0",
        description="应用版本"
    )
    
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="运行环境"
    )
    
    debug: bool = Field(
        default=True,
        description="是否启用调试模式"
    )
    
    # 服务器配置
    host: str = Field(
        default="0.0.0.0",
        description="服务器监听地址"
    )
    
    port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="服务器监听端口"
    )
    
    # API配置
    api_prefix: str = Field(
        default="/api/v1",
        description="API路径前缀"
    )
    
    docs_url: Optional[str] = Field(
        default="/docs",
        description="Swagger文档URL（None为禁用）"
    )
    
    redoc_url: Optional[str] = Field(
        default="/redoc", 
        description="ReDoc文档URL（None为禁用）"
    )
    
    openapi_url: Optional[str] = Field(
        default="/openapi.json",
        description="OpenAPI规范URL（None为禁用）"
    )
    
    # 数据库配置
    database_url: str = Field(
        default="sqlite:///./app.db",
        description="数据库连接URL"
    )
    
    database_pool_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="连接池大小"
    )
    
    database_max_overflow: int = Field(
        default=20,
        ge=0,
        le=100,
        description="连接池最大溢出连接数"
    )
    
    database_pool_recycle: int = Field(
        default=3600,
        ge=60,
        description="连接回收时间（秒）"
    )
    
    database_pool_pre_ping: bool = Field(
        default=True,
        description="连接前是否ping检查"
    )
    
    database_echo_sql: bool = Field(
        default=False,
        description="是否输出SQL查询日志"
    )
    
    database_alembic_ini_path: str = Field(
        default="alembic.ini",
        description="Alembic配置文件路径"
    )
    
    # 日志配置
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="日志级别"
    )
    
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    
    log_file_enabled: bool = Field(
        default=True,
        description="是否启用文件日志"
    )
    
    log_file_path: str = Field(
        default="logs/app.log",
        description="日志文件路径"
    )
    
    log_file_max_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        ge=1024,
        description="日志文件最大大小（字节）"
    )
    
    log_file_backup_count: int = Field(
        default=5,
        ge=1,
        le=20,
        description="日志文件备份数量"
    )
    
    log_structured_logging: bool = Field(
        default=True,
        description="是否启用结构化日志"
    )
    
    log_requests: bool = Field(
        default=True,
        description="是否记录请求日志"
    )
    
    log_request_body: bool = Field(
        default=False,
        description="是否记录请求体（敏感信息注意）"
    )
    
    # JWT配置
    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production",
        min_length=32,
        description="JWT密钥"
    )
    
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        ge=1,
        description="访问令牌过期时间（分钟）"
    )
    
    jwt_refresh_token_expire_days: int = Field(
        default=7,
        ge=1,
        description="刷新令牌过期时间（天）"
    )
    
    # CORS配置
    jwt_allow_origins: List[str] = Field(
        default=["*"],
        description="允许的跨域来源"
    )
    
    jwt_allow_methods: List[str] = Field(
        default=["*"],
        description="允许的HTTP方法"
    )
    
    jwt_allow_headers: List[str] = Field(
        default=["*"],
        description="允许的HTTP头"
    )
    
    jwt_allow_credentials: bool = Field(
        default=True,
        description="是否允许携带凭证"
    )
    
    # 扩展配置
    extra_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="额外配置项"
    )

    @validator("environment", pre=True)
    def validate_environment(cls, v: Union[str, Environment]) -> Environment:
        """验证环境配置"""
        if isinstance(v, str):
            v = v.lower()
            if v in ["dev", "develop", "development"]:
                return Environment.DEVELOPMENT
            elif v in ["test", "testing"]:
                return Environment.TESTING
            elif v in ["prod", "production"]:
                return Environment.PRODUCTION
        return v

    @validator("debug")
    def validate_debug_by_env(cls, v: bool, values: Dict[str, Any]) -> bool:
        """根据环境自动设置debug模式"""
        env = values.get("environment")
        if env == Environment.PRODUCTION:
            return False
        return v

    @validator("docs_url", "redoc_url", "openapi_url")
    def validate_docs_url_in_production(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Optional[str]:
        """生产环境禁用文档"""
        env = values.get("environment")
        if env == Environment.PRODUCTION and not values.get("debug", False):
            return None
        return v

    def get_database_url(self, async_driver: bool = True) -> str:
        """获取数据库连接URL"""
        url = self.database_url
        
        # 自动转换为异步驱动
        if async_driver:
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif url.startswith("mysql://"):
                url = url.replace("mysql://", "mysql+aiomysql://", 1)
            elif url.startswith("sqlite://"):
                url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        
        return url

    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment == Environment.DEVELOPMENT

    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.environment == Environment.TESTING

    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment == Environment.PRODUCTION

    def create_log_directory(self) -> None:
        """创建日志目录"""
        if self.log_file_enabled:
            log_path = Path(self.log_file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)


# 全局配置实例
settings = Settings()

# 确保日志目录存在
settings.create_log_directory()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings


def reload_settings() -> Settings:
    """重新加载配置"""
    global settings
    settings = Settings()
    settings.create_log_directory()
    return settings
