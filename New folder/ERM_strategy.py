# strategies/ERM_strategy.py

import pandas as pd
from strategies.strategy_base import StrategyBase

class EMARSIMACDStrategy(StrategyBase):
    def generate_signal(self, df: pd.DataFrame) -> str:
        try:
            # بررسی اینکه تمام ستون‌های موردنیاز وجود دارند
            required_cols = ["EMA_21", "RSI_14", "MACD", "MACD_signal"]
            if not all(col in df.columns for col in required_cols):
                print(f"⚠️ Missing columns in DataFrame: {required_cols}")
                return "NONE"

            # بررسی اینکه حداقل یک ردیف قابل تحلیل داریم
            if df.empty or len(df) < 2:
                return "NONE"

            latest = df.iloc[-1]
            previous = df.iloc[-2]

            # شروط خرید:
            if (
                latest["close"] > latest["EMA_21"] and
                latest["RSI_14"] > 50 and
                previous["MACD"] < previous["MACD_signal"] and
                latest["MACD"] > latest["MACD_signal"]
            ):
                return "BUY"

            # شروط فروش:
            elif (
                latest["close"] < latest["EMA_21"] and
                latest["RSI_14"] < 50 and
                previous["MACD"] > previous["MACD_signal"] and
                latest["MACD"] < latest["MACD_signal"]
            ):
                return "SELL"

            return "NONE"

        except Exception as e:
            print(f"❌ Strategy Error [{self.symbol} {self.timeframe}]: {e}")
            return "NONE"
