#!/usr/bin/env python3
"""
金额计算工具类

提供精确的金额计算、格式化、转换等功能
"""

from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN, ROUND_UP, Context
from typing import Union, Optional, Dict, Any
import re
from enum import Enum


class RoundingMode(Enum):
    """舍入模式"""
    HALF_UP = ROUND_HALF_UP      # 四舍五入
    DOWN = ROUND_DOWN            # 向下舍入
    UP = ROUND_UP                # 向上舍入


class Currency(Enum):
    """货币类型"""
    CNY = ("CNY", "¥", "人民币", 2)
    USD = ("USD", "$", "美元", 2)
    EUR = ("EUR", "€", "欧元", 2)
    JPY = ("JPY", "¥", "日元", 0)
    GBP = ("GBP", "£", "英镑", 2)
    HKD = ("HKD", "HK$", "港币", 2)
    
    def __init__(self, code: str, symbol: str, name: str, decimals: int):
        # 使用 _value_ 来存储元组值
        self._code = code
        self._symbol = symbol
        self._name = name
        self._decimals = decimals
    
    @property
    def code(self) -> str:
        return self._code
    
    @property
    def symbol(self) -> str:
        return self._symbol
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def decimals(self) -> int:
        return self._decimals


class Money:
    """金额类"""
    
    def __init__(
        self,
        amount: Union[str, int, float, Decimal],
        currency: Currency = Currency.CNY
    ):
        """
        初始化金额对象
        
        Args:
            amount: 金额值
            currency: 货币类型
        """
        self.currency = currency
        self.amount = self._normalize_amount(amount)
    
    def _normalize_amount(self, amount: Union[str, int, float, Decimal]) -> Decimal:
        """标准化金额"""
        if isinstance(amount, Decimal):
            return amount.quantize(
                Decimal('0.' + '0' * self.currency.decimals),
                rounding=ROUND_HALF_UP
            )
        
        # 处理字符串金额
        if isinstance(amount, str):
            # 移除货币符号和空格
            amount = re.sub(r'[^\d.-]', '', amount)
        
        decimal_amount = Decimal(str(amount))
        return decimal_amount.quantize(
            Decimal('0.' + '0' * self.currency.decimals),
            rounding=ROUND_HALF_UP
        )
    
    def __str__(self) -> str:
        return f"{self.currency.symbol}{self.amount}"
    
    def __repr__(self) -> str:
        return f"Money(amount={self.amount}, currency={self.currency.code})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def __lt__(self, other) -> bool:
        self._check_currency_compatibility(other)
        return self.amount < other.amount
    
    def __le__(self, other) -> bool:
        self._check_currency_compatibility(other)
        return self.amount <= other.amount
    
    def __gt__(self, other) -> bool:
        self._check_currency_compatibility(other)
        return self.amount > other.amount
    
    def __ge__(self, other) -> bool:
        self._check_currency_compatibility(other)
        return self.amount >= other.amount
    
    def __add__(self, other) -> 'Money':
        self._check_currency_compatibility(other)
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other) -> 'Money':
        self._check_currency_compatibility(other)
        return Money(self.amount - other.amount, self.currency)
    
    def __mul__(self, multiplier: Union[int, float, Decimal]) -> 'Money':
        return Money(self.amount * Decimal(str(multiplier)), self.currency)
    
    def __truediv__(self, divisor: Union[int, float, Decimal]) -> 'Money':
        return Money(self.amount / Decimal(str(divisor)), self.currency)
    
    def __neg__(self) -> 'Money':
        return Money(-self.amount, self.currency)
    
    def __abs__(self) -> 'Money':
        return Money(abs(self.amount), self.currency)
    
    def _check_currency_compatibility(self, other: 'Money'):
        """检查货币兼容性"""
        if not isinstance(other, Money):
            raise TypeError("Can only operate with another Money instance")
        if self.currency != other.currency:
            raise ValueError(f"Cannot operate between {self.currency.code} and {other.currency.code}")
    
    def is_zero(self) -> bool:
        """是否为零"""
        return self.amount == Decimal('0')
    
    def is_positive(self) -> bool:
        """是否为正数"""
        return self.amount > Decimal('0')
    
    def is_negative(self) -> bool:
        """是否为负数"""
        return self.amount < Decimal('0')
    
    def to_cents(self) -> int:
        """转换为分(整数)"""
        return int(self.amount * (10 ** self.currency.decimals))
    
    @classmethod
    def from_cents(cls, cents: int, currency: Currency = Currency.CNY) -> 'Money':
        """从分创建金额对象"""
        amount = Decimal(cents) / (10 ** currency.decimals)
        return cls(amount, currency)
    
    def format(
        self,
        show_symbol: bool = True,
        show_currency_code: bool = False,
        thousands_separator: str = ","
    ) -> str:
        """格式化金额显示"""
        # 格式化数字
        if thousands_separator:
            # 添加千位分隔符
            amount_str = f"{self.amount:,}"
            if thousands_separator != ",":
                amount_str = amount_str.replace(",", thousands_separator)
        else:
            amount_str = str(self.amount)
        
        # 添加货币符号
        result = ""
        if show_symbol:
            result = f"{self.currency.symbol}{amount_str}"
        else:
            result = amount_str
        
        # 添加货币代码
        if show_currency_code:
            result = f"{result} {self.currency.code}"
        
        return result
    
    def round(self, decimals: Optional[int] = None, rounding: RoundingMode = RoundingMode.HALF_UP) -> 'Money':
        """四舍五入"""
        if decimals is None:
            decimals = self.currency.decimals
        
        quantizer = Decimal('0.' + '0' * decimals)
        rounded_amount = self.amount.quantize(quantizer, rounding=rounding.value)
        return Money(rounded_amount, self.currency)


class MoneyUtils:
    """金额工具类"""
    
    @staticmethod
    def parse_money(
        money_str: str,
        currency: Currency = Currency.CNY
    ) -> Money:
        """解析金额字符串"""
        return Money(money_str, currency)
    
    @staticmethod
    def sum_money(money_list: list[Money]) -> Optional[Money]:
        """计算金额列表总和"""
        if not money_list:
            return None
        
        result = money_list[0]
        for money in money_list[1:]:
            result = result + money
        
        return result
    
    @staticmethod
    def average_money(money_list: list[Money]) -> Optional[Money]:
        """计算金额列表平均值"""
        if not money_list:
            return None
        
        total = MoneyUtils.sum_money(money_list)
        return total / len(money_list)
    
    @staticmethod
    def max_money(money_list: list[Money]) -> Optional[Money]:
        """获取最大金额"""
        if not money_list:
            return None
        return max(money_list)
    
    @staticmethod
    def min_money(money_list: list[Money]) -> Optional[Money]:
        """获取最小金额"""
        if not money_list:
            return None
        return min(money_list)
    
    @staticmethod
    def allocate_money(
        total: Money,
        ratios: list[Union[int, float, Decimal]]
    ) -> list[Money]:
        """按比例分配金额"""
        if not ratios:
            return []
        
        # 转换比例为Decimal
        decimal_ratios = [Decimal(str(ratio)) for ratio in ratios]
        total_ratio = sum(decimal_ratios)
        
        if total_ratio == 0:
            return [Money(0, total.currency) for _ in ratios]
        
        # 计算分配金额
        allocated = []
        remaining = total.amount
        
        for i, ratio in enumerate(decimal_ratios):
            if i == len(decimal_ratios) - 1:
                # 最后一个分配剩余金额，避免舍入误差
                allocated.append(Money(remaining, total.currency))
            else:
                amount = (total.amount * ratio / total_ratio).quantize(
                    Decimal('0.' + '0' * total.currency.decimals),
                    rounding=ROUND_DOWN
                )
                allocated.append(Money(amount, total.currency))
                remaining -= amount
        
        return allocated
    
    @staticmethod
    def calculate_percentage(
        amount: Money,
        percentage: Union[int, float, Decimal],
        rounding: RoundingMode = RoundingMode.HALF_UP
    ) -> Money:
        """计算百分比金额"""
        result = amount * (Decimal(str(percentage)) / 100)
        return result.round(rounding=rounding)
    
    @staticmethod
    def calculate_discount(
        original_price: Money,
        discount_rate: Union[int, float, Decimal]
    ) -> tuple[Money, Money]:
        """
        计算折扣
        
        Returns:
            tuple: (折扣金额, 折后价格)
        """
        discount_amount = MoneyUtils.calculate_percentage(original_price, discount_rate)
        final_price = original_price - discount_amount
        return discount_amount, final_price
    
    @staticmethod
    def calculate_tax(
        amount: Money,
        tax_rate: Union[int, float, Decimal],
        include_tax: bool = False
    ) -> tuple[Money, Money]:
        """
        计算税额
        
        Args:
            amount: 金额
            tax_rate: 税率(百分比)
            include_tax: 金额是否含税
            
        Returns:
            tuple: (税额, 含税总额) 或 (税额, 不含税金额)
        """
        tax_decimal = Decimal(str(tax_rate)) / 100
        
        if include_tax:
            # 含税价格计算不含税金额和税额
            net_amount = amount / (1 + tax_decimal)
            tax_amount = amount - net_amount
            return tax_amount.round(), net_amount.round()
        else:
            # 不含税价格计算税额和含税总额
            tax_amount = amount * tax_decimal
            total_amount = amount + tax_amount
            return tax_amount.round(), total_amount.round()
    
    @staticmethod
    def format_chinese_amount(amount: Money) -> str:
        """格式化中文大写金额"""
        if amount.currency != Currency.CNY:
            raise ValueError("Chinese amount formatting only supports CNY")
        
        digits = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
        units = ['', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿']
        
        amount_int = int(abs(amount.amount))
        amount_str = str(amount_int)
        
        if amount_int == 0:
            return "零元整"
        
        result = ""
        length = len(amount_str)
        
        for i, digit in enumerate(amount_str):
            digit_int = int(digit)
            unit_index = length - i - 1
            
            if digit_int != 0:
                result += digits[digit_int] + units[unit_index]
            elif unit_index == 4:  # 万位
                result += '万'
        
        # 处理小数部分
        decimal_part = amount.amount % 1
        if decimal_part > 0:
            jiao = int(decimal_part * 10) % 10
            fen = int(decimal_part * 100) % 10
            
            if jiao > 0:
                result += digits[jiao] + '角'
            if fen > 0:
                result += digits[fen] + '分'
        else:
            result += '整'
        
        result += '元'
        
        if amount.is_negative():
            result = '负' + result
        
        return result
    
    @staticmethod
    def convert_currency(
        amount: Money,
        target_currency: Currency,
        exchange_rate: Union[float, Decimal]
    ) -> Money:
        """货币转换"""
        converted_amount = amount.amount * Decimal(str(exchange_rate))
        return Money(converted_amount, target_currency)


# 便捷函数
def money(
    amount: Union[str, int, float, Decimal],
    currency: Currency = Currency.CNY
) -> Money:
    """创建金额对象"""
    return Money(amount, currency)


def cny(amount: Union[str, int, float, Decimal]) -> Money:
    """创建人民币金额对象"""
    return Money(amount, Currency.CNY)


def usd(amount: Union[str, int, float, Decimal]) -> Money:
    """创建美元金额对象"""
    return Money(amount, Currency.USD)
