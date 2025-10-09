#!/usr/bin/env python3
"""
日期工具类

提供常用的日期时间处理功能
"""

from datetime import datetime, date, timedelta, timezone
from typing import Optional, Union, List
import time
import calendar

# 兼容性处理：Python 3.9+ 使用 zoneinfo，否则使用 pytz
try:
    from zoneinfo import ZoneInfo
except ImportError:
    try:
        import pytz
        # 创建兼容的 ZoneInfo 类
        class ZoneInfo:
            def __init__(self, key):
                self.zone = pytz.timezone(key)
            
            def __call__(self, key):
                return pytz.timezone(key)
        
        ZoneInfo = lambda key: pytz.timezone(key)
    except ImportError:
        # 如果都没有，使用UTC作为默认
        ZoneInfo = lambda key: timezone.utc


class DateUtils:
    """日期时间工具类"""
    
    # 常用日期格式
    FORMAT_DATETIME = "%Y-%m-%d %H:%M:%S"
    FORMAT_DATE = "%Y-%m-%d"
    FORMAT_TIME = "%H:%M:%S"
    FORMAT_DATETIME_MS = "%Y-%m-%d %H:%M:%S.%f"
    FORMAT_ISO = "%Y-%m-%dT%H:%M:%S"
    FORMAT_ISO_MS = "%Y-%m-%dT%H:%M:%S.%f"
    FORMAT_COMPACT = "%Y%m%d%H%M%S"
    FORMAT_COMPACT_DATE = "%Y%m%d"
    
    # 中文格式
    FORMAT_CN_DATETIME = "%Y年%m月%d日 %H:%M:%S"
    FORMAT_CN_DATE = "%Y年%m月%d日"
    
    @staticmethod
    def now(timezone_name: str = "Asia/Shanghai") -> datetime:
        """获取当前时间"""
        tz = ZoneInfo(timezone_name)
        return datetime.now(tz)
    
    @staticmethod
    def utc_now() -> datetime:
        """获取UTC当前时间"""
        return datetime.now(timezone.utc)
    
    @staticmethod
    def today(timezone_name: str = "Asia/Shanghai") -> date:
        """获取今天日期"""
        return DateUtils.now(timezone_name).date()
    
    @staticmethod
    def format_datetime(
        dt: Optional[datetime] = None, 
        fmt: str = FORMAT_DATETIME,
        timezone_name: str = "Asia/Shanghai"
    ) -> str:
        """格式化日期时间"""
        if dt is None:
            dt = DateUtils.now(timezone_name)
        return dt.strftime(fmt)
    
    @staticmethod
    def format_date(
        d: Optional[date] = None,
        fmt: str = FORMAT_DATE
    ) -> str:
        """格式化日期"""
        if d is None:
            d = DateUtils.today()
        return d.strftime(fmt)
    
    @staticmethod
    def parse_datetime(
        date_str: str,
        fmt: str = FORMAT_DATETIME,
        timezone_name: Optional[str] = None
    ) -> datetime:
        """解析日期时间字符串"""
        dt = datetime.strptime(date_str, fmt)
        if timezone_name:
            tz = ZoneInfo(timezone_name)
            dt = dt.replace(tzinfo=tz)
        return dt
    
    @staticmethod
    def parse_date(date_str: str, fmt: str = FORMAT_DATE) -> date:
        """解析日期字符串"""
        return datetime.strptime(date_str, fmt).date()
    
    @staticmethod
    def timestamp() -> int:
        """获取当前时间戳(秒)"""
        return int(time.time())
    
    @staticmethod
    def timestamp_ms() -> int:
        """获取当前时间戳(毫秒)"""
        return int(time.time() * 1000)
    
    @staticmethod
    def from_timestamp(
        timestamp: Union[int, float],
        timezone_name: str = "Asia/Shanghai"
    ) -> datetime:
        """从时间戳创建datetime对象"""
        tz = ZoneInfo(timezone_name)
        return datetime.fromtimestamp(timestamp, tz)
    
    @staticmethod
    def to_timestamp(dt: datetime) -> int:
        """将datetime转换为时间戳"""
        return int(dt.timestamp())
    
    @staticmethod
    def add_days(dt: datetime, days: int) -> datetime:
        """增加天数"""
        return dt + timedelta(days=days)
    
    @staticmethod
    def add_hours(dt: datetime, hours: int) -> datetime:
        """增加小时数"""
        return dt + timedelta(hours=hours)
    
    @staticmethod
    def add_minutes(dt: datetime, minutes: int) -> datetime:
        """增加分钟数"""
        return dt + timedelta(minutes=minutes)
    
    @staticmethod
    def add_seconds(dt: datetime, seconds: int) -> datetime:
        """增加秒数"""
        return dt + timedelta(seconds=seconds)
    
    @staticmethod
    def diff_days(dt1: datetime, dt2: datetime) -> int:
        """计算两个日期的天数差"""
        return (dt1.date() - dt2.date()).days
    
    @staticmethod
    def diff_hours(dt1: datetime, dt2: datetime) -> float:
        """计算两个时间的小时差"""
        return (dt1 - dt2).total_seconds() / 3600
    
    @staticmethod
    def diff_minutes(dt1: datetime, dt2: datetime) -> float:
        """计算两个时间的分钟差"""
        return (dt1 - dt2).total_seconds() / 60
    
    @staticmethod
    def diff_seconds(dt1: datetime, dt2: datetime) -> float:
        """计算两个时间的秒差"""
        return (dt1 - dt2).total_seconds()
    
    @staticmethod
    def start_of_day(dt: datetime) -> datetime:
        """获取一天的开始时间 (00:00:00)"""
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def end_of_day(dt: datetime) -> datetime:
        """获取一天的结束时间 (23:59:59.999999)"""
        return dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    @staticmethod
    def start_of_month(dt: datetime) -> datetime:
        """获取月初时间"""
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def end_of_month(dt: datetime) -> datetime:
        """获取月末时间"""
        last_day = calendar.monthrange(dt.year, dt.month)[1]
        return dt.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
    
    @staticmethod
    def start_of_year(dt: datetime) -> datetime:
        """获取年初时间"""
        return dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def end_of_year(dt: datetime) -> datetime:
        """获取年末时间"""
        return dt.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    
    @staticmethod
    def is_weekend(dt: datetime) -> bool:
        """判断是否为周末"""
        return dt.weekday() >= 5  # 5=Saturday, 6=Sunday
    
    @staticmethod
    def is_workday(dt: datetime) -> bool:
        """判断是否为工作日"""
        return not DateUtils.is_weekend(dt)
    
    @staticmethod
    def get_weekday_name(dt: datetime, locale: str = "en") -> str:
        """获取星期名称"""
        weekdays = {
            "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "cn": ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        }
        return weekdays.get(locale, weekdays["en"])[dt.weekday()]
    
    @staticmethod
    def get_month_name(dt: datetime, locale: str = "en") -> str:
        """获取月份名称"""
        months = {
            "en": ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"],
            "cn": ["一月", "二月", "三月", "四月", "五月", "六月",
                   "七月", "八月", "九月", "十月", "十一月", "十二月"]
        }
        return months.get(locale, months["en"])[dt.month - 1]
    
    @staticmethod
    def get_date_range(
        start_date: Union[datetime, date],
        end_date: Union[datetime, date],
        step_days: int = 1
    ) -> List[date]:
        """获取日期范围列表"""
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime):
            end_date = end_date.date()
        
        dates = []
        current = start_date
        while current <= end_date:
            dates.append(current)
            current += timedelta(days=step_days)
        return dates
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """格式化时长"""
        if seconds < 60:
            return f"{seconds:.2f}秒"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}分钟"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f}小时"
        else:
            days = seconds / 86400
            return f"{days:.1f}天"
    
    @staticmethod
    def age_from_birthday(birthday: Union[datetime, date], reference_date: Optional[date] = None) -> int:
        """根据生日计算年龄"""
        if isinstance(birthday, datetime):
            birthday = birthday.date()
        if reference_date is None:
            reference_date = DateUtils.today()
        
        age = reference_date.year - birthday.year
        if reference_date.month < birthday.month or \
           (reference_date.month == birthday.month and reference_date.day < birthday.day):
            age -= 1
        return age
    
    @staticmethod
    def is_leap_year(year: int) -> bool:
        """判断是否为闰年"""
        return calendar.isleap(year)
    
    @staticmethod
    def days_in_month(year: int, month: int) -> int:
        """获取指定年月的天数"""
        return calendar.monthrange(year, month)[1]


# 便捷函数
def now(timezone_name: str = "Asia/Shanghai") -> datetime:
    """获取当前时间"""
    return DateUtils.now(timezone_name)


def utc_now() -> datetime:
    """获取UTC当前时间"""
    return DateUtils.utc_now()


def today(timezone_name: str = "Asia/Shanghai") -> date:
    """获取今天日期"""
    return DateUtils.today(timezone_name)


def format_duration(seconds: float) -> str:
    """格式化时长"""
    return DateUtils.format_duration(seconds)
