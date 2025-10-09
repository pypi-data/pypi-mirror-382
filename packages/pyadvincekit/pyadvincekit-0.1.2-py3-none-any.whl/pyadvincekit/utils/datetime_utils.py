"""
日期时间工具模块

提供日期时间处理的常用工具函数。
"""

from datetime import datetime, timedelta, timezone, date
from typing import Optional, Union
import pytz


class DateTimeUtils:
    """日期时间工具类"""
    
    # 常用时区
    UTC = timezone.utc
    BEIJING = pytz.timezone('Asia/Shanghai')
    NEW_YORK = pytz.timezone('America/New_York')
    LONDON = pytz.timezone('Europe/London')
    TOKYO = pytz.timezone('Asia/Tokyo')
    
    @staticmethod
    def now(tz: Optional[timezone] = None) -> datetime:
        """
        获取当前时间
        
        Args:
            tz: 时区，默认为UTC
            
        Returns:
            当前时间
        """
        if tz is None:
            tz = DateTimeUtils.UTC
        return datetime.now(tz)
    
    @staticmethod
    def utc_now() -> datetime:
        """获取当前UTC时间"""
        return datetime.now(DateTimeUtils.UTC)
    
    @staticmethod
    def today(tz: Optional[timezone] = None) -> date:
        """
        获取今天的日期
        
        Args:
            tz: 时区，默认为UTC
            
        Returns:
            今天的日期
        """
        return DateTimeUtils.now(tz).date()
    
    @staticmethod
    def timestamp_to_datetime(timestamp: Union[int, float], tz: Optional[timezone] = None) -> datetime:
        """
        时间戳转datetime
        
        Args:
            timestamp: 时间戳（秒）
            tz: 时区，默认为UTC
            
        Returns:
            datetime对象
        """
        if tz is None:
            tz = DateTimeUtils.UTC
        return datetime.fromtimestamp(timestamp, tz)
    
    @staticmethod
    def datetime_to_timestamp(dt: datetime) -> float:
        """
        datetime转时间戳
        
        Args:
            dt: datetime对象
            
        Returns:
            时间戳（秒）
        """
        return dt.timestamp()
    
    @staticmethod
    def str_to_datetime(
        date_string: str, 
        format_string: str = "%Y-%m-%d %H:%M:%S",
        tz: Optional[timezone] = None
    ) -> datetime:
        """
        字符串转datetime
        
        Args:
            date_string: 日期字符串
            format_string: 格式字符串
            tz: 时区
            
        Returns:
            datetime对象
        """
        dt = datetime.strptime(date_string, format_string)
        if tz:
            dt = dt.replace(tzinfo=tz)
        return dt
    
    @staticmethod
    def datetime_to_str(
        dt: datetime, 
        format_string: str = "%Y-%m-%d %H:%M:%S"
    ) -> str:
        """
        datetime转字符串
        
        Args:
            dt: datetime对象
            format_string: 格式字符串
            
        Returns:
            日期字符串
        """
        return dt.strftime(format_string)
    
    @staticmethod
    def iso_to_datetime(iso_string: str) -> datetime:
        """
        ISO字符串转datetime
        
        Args:
            iso_string: ISO格式字符串
            
        Returns:
            datetime对象
        """
        return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    
    @staticmethod
    def datetime_to_iso(dt: datetime) -> str:
        """
        datetime转ISO字符串
        
        Args:
            dt: datetime对象
            
        Returns:
            ISO格式字符串
        """
        return dt.isoformat()
    
    @staticmethod
    def convert_timezone(dt: datetime, target_tz: timezone) -> datetime:
        """
        转换时区
        
        Args:
            dt: datetime对象
            target_tz: 目标时区
            
        Returns:
            转换后的datetime对象
        """
        return dt.astimezone(target_tz)
    
    @staticmethod
    def add_time(
        dt: datetime, 
        days: int = 0, 
        hours: int = 0, 
        minutes: int = 0, 
        seconds: int = 0
    ) -> datetime:
        """
        添加时间
        
        Args:
            dt: 基准时间
            days: 天数
            hours: 小时数
            minutes: 分钟数
            seconds: 秒数
            
        Returns:
            添加后的时间
        """
        delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        return dt + delta
    
    @staticmethod
    def subtract_time(
        dt: datetime, 
        days: int = 0, 
        hours: int = 0, 
        minutes: int = 0, 
        seconds: int = 0
    ) -> datetime:
        """
        减去时间
        
        Args:
            dt: 基准时间
            days: 天数
            hours: 小时数
            minutes: 分钟数
            seconds: 秒数
            
        Returns:
            减去后的时间
        """
        delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        return dt - delta
    
    @staticmethod
    def time_difference(dt1: datetime, dt2: datetime) -> timedelta:
        """
        计算时间差
        
        Args:
            dt1: 时间1
            dt2: 时间2
            
        Returns:
            时间差
        """
        return dt1 - dt2
    
    @staticmethod
    def days_between(dt1: datetime, dt2: datetime) -> int:
        """
        计算两个日期间的天数
        
        Args:
            dt1: 日期1
            dt2: 日期2
            
        Returns:
            天数差
        """
        return (dt1.date() - dt2.date()).days
    
    @staticmethod
    def is_weekend(dt: datetime) -> bool:
        """
        判断是否为周末
        
        Args:
            dt: datetime对象
            
        Returns:
            是否为周末
        """
        return dt.weekday() >= 5  # 5=Saturday, 6=Sunday
    
    @staticmethod
    def get_week_start(dt: datetime) -> datetime:
        """
        获取周的开始时间（周一）
        
        Args:
            dt: datetime对象
            
        Returns:
            周的开始时间
        """
        days_since_monday = dt.weekday()
        week_start = dt - timedelta(days=days_since_monday)
        return week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def get_month_start(dt: datetime) -> datetime:
        """
        获取月的开始时间
        
        Args:
            dt: datetime对象
            
        Returns:
            月的开始时间
        """
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def get_year_start(dt: datetime) -> datetime:
        """
        获取年的开始时间
        
        Args:
            dt: datetime对象
            
        Returns:
            年的开始时间
        """
        return dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def format_duration(seconds: Union[int, float]) -> str:
        """
        格式化持续时间
        
        Args:
            seconds: 秒数
            
        Returns:
            格式化的时间字符串
        """
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
    def humanize_datetime(dt: datetime, reference: Optional[datetime] = None) -> str:
        """
        人性化时间显示
        
        Args:
            dt: 目标时间
            reference: 参考时间，默认为当前时间
            
        Returns:
            人性化的时间字符串
        """
        if reference is None:
            reference = DateTimeUtils.utc_now()
        
        diff = reference - dt
        total_seconds = abs(diff.total_seconds())
        
        if total_seconds < 60:
            return "刚刚"
        elif total_seconds < 3600:
            minutes = int(total_seconds / 60)
            return f"{minutes}分钟前" if diff.total_seconds() > 0 else f"{minutes}分钟后"
        elif total_seconds < 86400:
            hours = int(total_seconds / 3600)
            return f"{hours}小时前" if diff.total_seconds() > 0 else f"{hours}小时后"
        elif total_seconds < 2592000:  # 30 days
            days = int(total_seconds / 86400)
            return f"{days}天前" if diff.total_seconds() > 0 else f"{days}天后"
        else:
            return DateTimeUtils.datetime_to_str(dt, "%Y-%m-%d")


# 便捷函数
def now(tz: Optional[timezone] = None) -> datetime:
    """获取当前时间"""
    return DateTimeUtils.now(tz)


def utc_now() -> datetime:
    """获取当前UTC时间"""
    return DateTimeUtils.utc_now()


def today(tz: Optional[timezone] = None) -> date:
    """获取今天的日期"""
    return DateTimeUtils.today(tz)


def timestamp_to_datetime(timestamp: Union[int, float], tz: Optional[timezone] = None) -> datetime:
    """时间戳转datetime"""
    return DateTimeUtils.timestamp_to_datetime(timestamp, tz)


def datetime_to_timestamp(dt: datetime) -> float:
    """datetime转时间戳"""
    return DateTimeUtils.datetime_to_timestamp(dt)


def format_duration(seconds: Union[int, float]) -> str:
    """格式化持续时间"""
    return DateTimeUtils.format_duration(seconds)


def humanize_datetime(dt: datetime, reference: Optional[datetime] = None) -> str:
    """人性化时间显示"""
    return DateTimeUtils.humanize_datetime(dt, reference)












