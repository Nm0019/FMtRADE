# strategies/strategy_base.py

from abc import ABC, abstractmethod
import pandas as pd

class StrategyBase(ABC):
    """
    کلاس پایه برای پیاده‌سازی هر استراتژی سیگنال‌دهی
    """

    def __init__(self, symbol: str, timeframe: str, params: dict = None):
        """
        :param symbol: نام نماد معاملاتی (مثلاً BTCUSD)
        :param timeframe: تایم‌فریم (مثل M5)
        :param params: تنظیمات خاص این استراتژی
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.params = params or {}

    @abstractmethod
    def generate_signal(self, df: pd.DataFrame) -> str:
        """
        بررسی وضعیت بازار و تولید سیگنال
        باید یکی از 'BUY', 'SELL' یا 'NONE' را برگرداند
        :param df: دیتافریم کامل با ستون‌های اندیکاتورها
        :return: سیگنال نهایی
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} symbol={self.symbol} tf={self.timeframe}>"
