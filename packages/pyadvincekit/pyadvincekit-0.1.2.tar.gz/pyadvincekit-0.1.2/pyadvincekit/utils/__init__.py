"""
工具函数模块

提供常用的工具函数和辅助类。
"""

# 基础工具函数
from pyadvincekit.utils.common import generate_uuid, datetime_to_str, str_to_datetime

# 安全工具
from pyadvincekit.utils.security import (
    SecurityUtils, SymmetricEncryption,
    generate_secret_key, generate_random_string,
    hash_password, verify_password,
    md5_hash, sha256_hash,
    encrypt_data, decrypt_data,
)

# 日期时间工具
from pyadvincekit.utils.datetime_utils import (
    DateTimeUtils,
    now, utc_now, today,
    timestamp_to_datetime, datetime_to_timestamp,
    format_duration, humanize_datetime,
)

# 数据验证工具
from pyadvincekit.utils.validators import (
    Validators, DataValidator, ValidationError,
    validate_email, validate_phone, validate_url,
    validate_password_strength, create_validator,
)

# 第二阶段新增工具类
from pyadvincekit.utils.http_utils import (
    HTTPClient, HTTPUtils, APIClient,
    create_http_client, create_api_client
)
from pyadvincekit.utils.money_utils import (
    Money, MoneyUtils, Currency, RoundingMode,
    money, cny, usd
)
from pyadvincekit.utils.cron_parser import (
    CronExpression, CronParseError, parse_cron_expression, 
    get_next_cron_time, validate_cron_expression
)

__all__ = [
    # 基础工具
    "generate_uuid",
    "datetime_to_str", 
    "str_to_datetime",
    
    # 安全工具
    "SecurityUtils",
    "SymmetricEncryption", 
    "generate_secret_key",
    "generate_random_string",
    "hash_password",
    "verify_password",
    "md5_hash",
    "sha256_hash",
    "encrypt_data",
    "decrypt_data",
    
    # 日期时间工具
    "DateTimeUtils",
    "now",
    "utc_now",
    "today",
    "timestamp_to_datetime",
    "datetime_to_timestamp",
    "format_duration",
    "humanize_datetime",
    
    # 数据验证工具
    "Validators",
    "DataValidator",
    "ValidationError",
    "validate_email",
    "validate_phone",
    "validate_url",
    "validate_password_strength",
    "create_validator",
    
    # HTTP工具
    "HTTPClient", "HTTPUtils", "APIClient",
    "create_http_client", "create_api_client",
    
    # 金额工具
    "Money", "MoneyUtils", "Currency", "RoundingMode",
    "money", "cny", "usd",
    
    # Cron表达式解析工具
    "CronExpression", "CronParseError", "parse_cron_expression",
    "get_next_cron_time", "validate_cron_expression",
]
