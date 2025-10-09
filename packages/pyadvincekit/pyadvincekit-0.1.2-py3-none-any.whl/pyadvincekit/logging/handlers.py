"""
日志处理器模块

提供结构化日志配置和自定义日志处理器。
"""

import json
import logging
import logging.handlers
import sys
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Union

import structlog
from structlog import configure, get_logger
from structlog.processors import JSONRenderer, TimeStamper, add_log_level
from structlog.stdlib import  filter_by_level,add_logger_name

from pyadvincekit.core.config import Settings, get_settings

# 🔥 修复 Windows 控制台中文编码问题（在模块导入时立即执行）
def _fix_console_encoding():
    """修复控制台编码问题"""
    if sys.platform == 'win32':
        # 设置控制台代码页为 UTF-8
        try:
            os.system('chcp 65001 > nul 2>&1')
        except:
            pass
        
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

# 立即执行编码修复
_fix_console_encoding()


class ChineseJSONRenderer:
    """支持中文的JSON渲染器"""
    
    def __init__(self, **json_kw):
        """
        初始化中文JSON渲染器
        
        Args:
            **json_kw: 传递给json.dumps的参数
        """
        self._json_kw = {
            'ensure_ascii': False,  # 🔥 关键：不转义非ASCII字符
            'separators': (',', ':'),
            **json_kw
        }
    
    def __call__(self, logger, method_name, event_dict):
        """渲染事件字典为JSON字符串"""
        return json.dumps(event_dict, **self._json_kw)


class JSONFormatter(logging.Formatter):
    """JSON格式化器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为JSON"""
        # 🔥 使用本地时区而不是UTC，保持与控制台日志一致
        local_dt = datetime.fromtimestamp(record.created)
        log_data = {
            "timestamp": local_dt.isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }
        
        # 添加额外字段
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # 添加请求ID（如果存在）
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        # 🔥 确保中文字符正确显示
        return json.dumps(log_data, ensure_ascii=False, default=str, separators=(',', ':'))


class ColoredFormatter(logging.Formatter):
    """彩色控制台格式化器"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化带颜色的日志"""
        # 获取颜色
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # 格式化时间
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # 构建日志消息
        # 🔥 确保中文字符正确显示
        log_message = record.getMessage()
        message = f"{color}[{timestamp}] {record.levelname:<8}{reset} "
        message += f"{color}{record.name}:{record.lineno}{reset} - "
        message += f"{log_message}"
        
        # 添加请求ID（如果存在）
        if hasattr(record, "request_id"):
            message += f" [RequestID: {record.request_id}]"
        
        # 添加异常信息
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"
        
        return message


class RequestIDFilter(logging.Filter):
    """请求ID过滤器"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """添加请求ID到日志记录"""
        # 尝试从上下文获取请求ID
        request_id = getattr(record, "request_id", None)
        if not request_id:
            # 从当前上下文变量获取（如果设置了）
            try:
                import contextvars
                request_id_var = contextvars.ContextVar('request_id', default=None)
                request_id = request_id_var.get()
            except (ImportError, LookupError):
                request_id = None
        
        record.request_id = request_id or "unknown"
        return True


class LoggingSetup:
    """日志系统设置类"""
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self._configured = False
    
    def setup_logging(self) -> None:
        """设置日志系统"""
        if self._configured:
            return
        
        # 设置根日志器
        self._setup_root_logger()
        
        # 设置结构化日志
        if self.settings.log_structured_logging:
            self._setup_structlog()
        
        # 设置文件日志
        if self.settings.log_file_enabled:
            self._setup_file_logging()
        
        # 设置控制台日志
        self._setup_console_logging()
        
        self._configured = True
    
    def _setup_root_logger(self) -> None:
        """设置根日志器"""
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.settings.log_level.upper()))
        
        # 清除现有处理器
        root_logger.handlers.clear()
    
    def _setup_structlog(self) -> None:
        """设置结构化日志"""
        # 配置structlog处理器
        processors = [
            filter_by_level,
            add_logger_name,
            # 🔥 使用本地时区而不是UTC，保持时间一致性
            TimeStamper(fmt="iso", utc=False),
            add_log_level,
        ]
        
        # 根据环境选择渲染器
        if self.settings.is_development():
            # 开发环境使用控制台渲染器
            processors.append(structlog.dev.ConsoleRenderer(colors=True))
        else:
            # 🔥 生产环境使用支持中文的JSON渲染器
            processors.append(ChineseJSONRenderer())
        
        configure(
            processors=processors,
            wrapper_class=structlog.make_filtering_bound_logger(
                getattr(logging, self.settings.log_level.upper())
            ),
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    
    def _setup_file_logging(self) -> None:
        """设置文件日志"""
        log_file_path = Path(self.settings.log_file_path)
        
        # 确保日志目录存在
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建文件处理器（支持轮转）
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file_path,
            maxBytes=self.settings.log_file_max_size,
            backupCount=self.settings.log_file_backup_count,
            encoding='utf-8'
        )
        
        # 设置格式化器
        if self.settings.log_structured_logging:
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(self.settings.log_format)
        
        file_handler.setFormatter(formatter)
        file_handler.addFilter(RequestIDFilter())
        
        # 添加到根日志器
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
    
    def _setup_console_logging(self) -> None:
        """设置控制台日志"""
        # 确保控制台输出使用 UTF-8 编码
        console_handler = logging.StreamHandler(sys.stdout)
        
        # 🔥 修复中文编码问题：设置控制台编码
        if hasattr(console_handler.stream, 'reconfigure'):
            # Python 3.7+
            try:
                console_handler.stream.reconfigure(encoding='utf-8')
            except (AttributeError, ValueError):
                pass
        
        # 根据环境选择格式化器
        if self.settings.is_development():
            formatter = ColoredFormatter()
        elif self.settings.log_structured_logging:
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(self.settings.log_format)
        
        console_handler.setFormatter(formatter)
        console_handler.addFilter(RequestIDFilter())
        
        # 添加到根日志器
        root_logger = logging.getLogger()
        root_logger.addHandler(console_handler)
    
    def get_logger(self, name: str) -> Union[logging.Logger, structlog.BoundLogger]:
        """获取日志器"""
        if not self._configured:
            self.setup_logging()
        
        if self.settings.log_structured_logging:
            return structlog.get_logger(name)
        else:
            return logging.getLogger(name)
    
    def set_request_context(self, request_id: str, **kwargs) -> None:
        """设置请求上下文"""
        try:
            import contextvars
            request_id_var = contextvars.ContextVar('request_id')
            request_id_var.set(request_id)
            
            # 设置其他上下文变量
            for key, value in kwargs.items():
                context_var = contextvars.ContextVar(key)
                context_var.set(value)
        except ImportError:
            pass


# 全局日志设置实例
_logging_setup: Optional[LoggingSetup] = None


def get_logging_setup() -> LoggingSetup:
    """获取日志设置实例"""
    global _logging_setup
    if _logging_setup is None:
        _logging_setup = LoggingSetup()
    return _logging_setup


def setup_logging(settings: Optional[Settings] = None) -> None:
    """设置日志系统（便捷函数）"""
    logging_setup = LoggingSetup(settings)
    logging_setup.setup_logging()


def get_logger(name: str) -> Union[logging.Logger, structlog.BoundLogger]:
    """获取日志器（便捷函数）"""
    logging_setup = get_logging_setup()
    return logging_setup.get_logger(name)


def set_request_context(request_id: str, **kwargs) -> None:
    """设置请求上下文（便捷函数）"""
    logging_setup = get_logging_setup()
    logging_setup.set_request_context(request_id, **kwargs)


# 预配置的日志器实例
logger = get_logger(__name__)
