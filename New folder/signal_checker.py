# strategies/signal_checker.py

import pandas as pd
from strategies.strategy_base import StrategyBase

class EMARsiStrategy(StrategyBase):
    """
    استراتژی ترکیبی EMA و RSI برای تولید سیگنال
    منطق:
      BUY  → وقتی RSI < 30 و قیمت بالای EMA
      SELL → وقتی RSI > 70 و قیمت زیر EMA
    """

    def generate_signal(self, df: pd.DataFrame) -> str:
        rsi_col = self.params.get("rsi_col", "RSI_14")
        ema_col = self.params.get("ema_col", "EMA_21")
        price_col = self.params.get("price_col", "close")

        if df.empty or rsi_col not in df.columns or ema_col not in df.columns or price_col not in df.columns:
            return "NONE"

        latest = df.iloc[-1]

        if latest[rsi_col] < 30 and latest[price_col] > latest[ema_col]:
            return "BUY"
        elif latest[rsi_col] > 70 and latest[price_col] < latest[ema_col]:
            return "SELL"
        else:
            return "NONE"
