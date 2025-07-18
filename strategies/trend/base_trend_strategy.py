# strategies/trend/base_trend_strategy.py
from abc import ABC, abstractmethod
import pandas as pd

class BaseTrendStrategy(ABC):
    def __init__(self, symbol: str, timeframe: str, config: dict = None):
        self.symbol = symbol
        self.timeframe = timeframe
        self.config = config or {}

    @abstractmethod
    def detect_trend(self, df: pd.DataFrame) -> dict:
        """
        اجرای استراتژی تشخیص روند.
        خروجی: dict شامل:
        {
            "trend": "up" | "down" | "sideways",
            "score": float,
            "confidence": float (0-1),
            "details": str یا dict برای توضیحات
        }
        """
        pass
