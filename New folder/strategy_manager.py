import pandas as pd
from database.db_operations import fetch_recent_data
from strategies.combined_rsi_macd import CombinedRSIMACDStrategy  # استراتژی جدید
from config import SUPPORTED_TIMEFRAMES, TIMEFRAME_MAP

def evaluate_strategy(symbol: str, timeframe: str) -> str:
    try:
        df_rows = fetch_recent_data(symbol, timeframe, limit=1000)
        df = pd.DataFrame(df_rows, columns=["time", "open", "high", "low", "close", "volume"])
        if df.empty:
            return "NONE"

        strategy = CombinedRSIMACDStrategy(symbol, timeframe)
        signal_dict = strategy.evaluate(df)

        # سیگنال برمی‌گردد: 1=BUY، -1=SELL، 0=NONE
        signal = signal_dict.get("signal", 0)
        if signal == 1:
            return "BUY"
        elif signal == -1:
            return "SELL"
        else:
            return "NONE"

    except Exception as e:
        print(f"❌ Error in strategy for {symbol} [{timeframe}]: {e}")
        return "NONE"
