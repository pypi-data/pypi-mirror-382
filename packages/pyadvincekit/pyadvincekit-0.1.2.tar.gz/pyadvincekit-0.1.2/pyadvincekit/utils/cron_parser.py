#!/usr/bin/env python3
"""
Cron 表达式解析器

支持标准的 cron 表达式格式：
* * * * * （分钟 小时 日期 月份 星期）

扩展支持：
- 秒级精度：* * * * * * （秒 分钟 小时 日期 月份 星期）
- 特殊表达式：@yearly, @monthly, @weekly, @daily, @hourly
"""

import re
from datetime import datetime, timedelta
from typing import List, Set, Optional, Union
from calendar import monthrange

class CronParseError(Exception):
    """Cron表达式解析错误"""
    pass

class CronField:
    """Cron字段解析器"""
    
    def __init__(self, min_val: int, max_val: int, name: str):
        self.min_val = min_val
        self.max_val = max_val
        self.name = name
    
    def parse(self, field: str) -> Set[int]:
        """解析cron字段"""
        if field == "*":
            return set(range(self.min_val, self.max_val + 1))
        
        values = set()
        
        # 处理逗号分隔的多个值
        for part in field.split(","):
            part = part.strip()
            
            # 处理步长 (*/5, 1-10/2)
            if "/" in part:
                range_part, step_part = part.split("/", 1)
                try:
                    step = int(step_part)
                except ValueError:
                    raise CronParseError(f"Invalid step value in {self.name}: {step_part}")
                
                if step <= 0:
                    raise CronParseError(f"Step must be positive in {self.name}: {step}")
                
                if range_part == "*":
                    start, end = self.min_val, self.max_val
                elif "-" in range_part:
                    start_str, end_str = range_part.split("-", 1)
                    start, end = int(start_str), int(end_str)
                else:
                    start = int(range_part)
                    end = self.max_val
                
                values.update(range(start, end + 1, step))
            
            # 处理范围 (1-5)
            elif "-" in part:
                start_str, end_str = part.split("-", 1)
                try:
                    start, end = int(start_str), int(end_str)
                except ValueError:
                    raise CronParseError(f"Invalid range in {self.name}: {part}")
                
                if start > end:
                    raise CronParseError(f"Invalid range in {self.name}: start > end ({start} > {end})")
                
                values.update(range(start, end + 1))
            
            # 处理单个值
            else:
                try:
                    value = int(part)
                except ValueError:
                    raise CronParseError(f"Invalid value in {self.name}: {part}")
                
                values.add(value)
        
        # 验证值的范围
        for value in values:
            if not (self.min_val <= value <= self.max_val):
                raise CronParseError(
                    f"Value {value} out of range for {self.name} "
                    f"(valid range: {self.min_val}-{self.max_val})"
                )
        
        return values

class CronExpression:
    """Cron表达式解析器"""
    
    # 预定义的特殊表达式
    SPECIAL_EXPRESSIONS = {
        "@yearly": "0 0 1 1 *",
        "@annually": "0 0 1 1 *", 
        "@monthly": "0 0 1 * *",
        "@weekly": "0 0 * * 0",
        "@daily": "0 0 * * *",
        "@midnight": "0 0 * * *",
        "@hourly": "0 * * * *"
    }
    
    def __init__(self, expression: str):
        self.original_expression = expression.strip()
        self.expression = self._normalize_expression(expression)
        
        # 解析字段
        self.fields = self._parse_fields()
        
    def _normalize_expression(self, expression: str) -> str:
        """标准化表达式"""
        expression = expression.strip()
        
        # 处理特殊表达式
        if expression.lower() in self.SPECIAL_EXPRESSIONS:
            return self.SPECIAL_EXPRESSIONS[expression.lower()]
        
        return expression
    
    def _parse_fields(self) -> dict:
        """解析所有字段"""
        parts = self.expression.split()
        
        if len(parts) == 5:
            # 标准5字段格式：分 时 日 月 周
            minute, hour, day, month, weekday = parts
            second_values = {0}  # 默认在0秒执行
        elif len(parts) == 6:
            # 6字段格式：秒 分 时 日 月 周
            second, minute, hour, day, month, weekday = parts
            second_field = CronField(0, 59, "second")
            second_values = second_field.parse(second)
        else:
            raise CronParseError(
                f"Invalid cron expression: {self.expression}. "
                f"Expected 5 or 6 fields, got {len(parts)}"
            )
        
        # 定义字段解析器
        minute_field = CronField(0, 59, "minute")
        hour_field = CronField(0, 23, "hour") 
        day_field = CronField(1, 31, "day")
        month_field = CronField(1, 12, "month")
        weekday_field = CronField(0, 7, "weekday")  # 0和7都表示周日
        
        # 解析各字段
        fields = {
            "second": second_values,
            "minute": minute_field.parse(minute),
            "hour": hour_field.parse(hour),
            "day": day_field.parse(day),
            "month": month_field.parse(month),
            "weekday": weekday_field.parse(weekday)
        }
        
        # 处理周日的特殊情况（0和7都表示周日）
        if 7 in fields["weekday"]:
            fields["weekday"].add(0)
            fields["weekday"].remove(7)
        
        return fields
    
    def get_next_run_time(self, from_time: Optional[datetime] = None) -> datetime:
        """获取下次执行时间"""
        if from_time is None:
            from_time = datetime.now()
        
        # 从下一分钟开始查找（避免重复执行）
        next_time = from_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
        
        # 最多查找4年（防止无限循环）
        max_iterations = 366 * 24 * 60 * 4
        iterations = 0
        
        while iterations < max_iterations:
            if self.matches(next_time):
                return next_time
            
            next_time += timedelta(minutes=1)
            iterations += 1
        
        raise CronParseError(f"Could not find next execution time for: {self.original_expression}")
    
    def matches(self, dt: datetime) -> bool:
        """检查给定时间是否匹配cron表达式"""
        # 检查秒
        if dt.second not in self.fields["second"]:
            return False
        
        # 检查分钟
        if dt.minute not in self.fields["minute"]:
            return False
        
        # 检查小时
        if dt.hour not in self.fields["hour"]:
            return False
        
        # 检查月份
        if dt.month not in self.fields["month"]:
            return False
        
        # 检查日期和星期（OR关系）
        day_match = dt.day in self.fields["day"]
        weekday_match = dt.weekday() in self._convert_weekday(self.fields["weekday"])
        
        # 如果day和weekday都不是通配符，则需要满足其中一个
        day_is_wildcard = self.fields["day"] == set(range(1, 32))
        weekday_is_wildcard = self.fields["weekday"] == set(range(0, 8))
        
        if day_is_wildcard and weekday_is_wildcard:
            return True
        elif day_is_wildcard:
            return weekday_match
        elif weekday_is_wildcard:
            return day_match
        else:
            return day_match or weekday_match
    
    def _convert_weekday(self, cron_weekdays: Set[int]) -> Set[int]:
        """转换cron的星期表示到Python的星期表示
        
        Cron: 0=Sunday, 1=Monday, ..., 6=Saturday
        Python: 0=Monday, 1=Tuesday, ..., 6=Sunday
        """
        python_weekdays = set()
        for cron_day in cron_weekdays:
            if cron_day == 0:  # Sunday
                python_weekdays.add(6)
            else:  # Monday-Saturday
                python_weekdays.add(cron_day - 1)
        
        return python_weekdays
    
    def get_description(self) -> str:
        """获取表达式的人类可读描述"""
        if self.original_expression.lower() in self.SPECIAL_EXPRESSIONS:
            return {
                "@yearly": "每年执行一次 (1月1日 00:00)",
                "@annually": "每年执行一次 (1月1日 00:00)",
                "@monthly": "每月执行一次 (每月1日 00:00)",
                "@weekly": "每周执行一次 (周日 00:00)",
                "@daily": "每天执行一次 (00:00)",
                "@midnight": "每天执行一次 (00:00)",
                "@hourly": "每小时执行一次 (:00分)"
            }.get(self.original_expression.lower(), "")
        
        # 构建描述
        parts = []
        
        if len(self.fields["second"]) == 1 and 0 in self.fields["second"]:
            second_desc = ""
        else:
            second_desc = f"秒:{self._format_field_desc(self.fields['second'])}"
        
        minute_desc = f"分:{self._format_field_desc(self.fields['minute'])}"
        hour_desc = f"时:{self._format_field_desc(self.fields['hour'])}"
        day_desc = f"日:{self._format_field_desc(self.fields['day'])}"
        month_desc = f"月:{self._format_field_desc(self.fields['month'])}"
        weekday_desc = f"周:{self._format_weekday_desc(self.fields['weekday'])}"
        
        if second_desc:
            parts.append(second_desc)
        parts.extend([minute_desc, hour_desc, day_desc, month_desc, weekday_desc])
        
        return " ".join(parts)
    
    def _format_field_desc(self, values: Set[int]) -> str:
        """格式化字段描述"""
        if len(values) == 1:
            return str(list(values)[0])
        elif len(values) <= 5:
            return ",".join(map(str, sorted(values)))
        else:
            return f"[{len(values)}个值]"
    
    def _format_weekday_desc(self, values: Set[int]) -> str:
        """格式化星期描述"""
        weekday_names = {0: "日", 1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六"}
        
        if len(values) == 1:
            return weekday_names.get(list(values)[0], str(list(values)[0]))
        elif len(values) <= 3:
            names = [weekday_names.get(v, str(v)) for v in sorted(values)]
            return ",".join(names)
        else:
            return f"[{len(values)}天]"

def parse_cron_expression(expression: str) -> CronExpression:
    """解析cron表达式"""
    try:
        return CronExpression(expression)
    except Exception as e:
        raise CronParseError(f"Failed to parse cron expression '{expression}': {str(e)}")

def get_next_cron_time(expression: str, from_time: Optional[datetime] = None) -> datetime:
    """获取cron表达式的下次执行时间"""
    cron = parse_cron_expression(expression)
    return cron.get_next_run_time(from_time)

def validate_cron_expression(expression: str) -> bool:
    """验证cron表达式是否有效"""
    try:
        parse_cron_expression(expression)
        return True
    except CronParseError:
        return False





