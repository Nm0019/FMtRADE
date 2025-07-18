# strategies/strategy_runner.py

from multiprocessing import Pool, cpu_count, Manager
from database.symbols_meta import get_all_registered_symbols
from config import SUPPORTED_TIMEFRAMES, TIMEFRAME_MAP

from strategies.combined_rsi_macd import CombinedRSIMACDStrategy
import pandas as pd
from database.db_operations import fetch_recent_data

def run_strategy_for_symbol(symbol):
    VOTING_FRAMES = ["M1", "M5", "M30","H1","H4"]


    try:
        signals = []

        # بررسی همه تایم‌فریم‌های موردنظر (مثلاً SUPPORTED_TIMEFRAMES یا VOTING_FRAMES)
        for tf in VOTING_FRAMES:
            df_rows = fetch_recent_data(symbol, tf, limit=1000)
            df = pd.DataFrame(df_rows, columns=["time", "open", "high", "low", "close", "volume"])
            if df.empty:
                continue

            strategy = CombinedRSIMACDStrategy(symbol, tf)
            signal = strategy.generate_signal(df)

            if signal != "NONE":
                signals.append((signal, tf))

        # اگر هیچ سیگنالی نبود
        if not signals:
            return ("NONE", symbol, None)

        # فقط اولین سیگنال را می‌توان برگرداند یا همه را برگرداند (بستگی به نیاز شما)
        # اینجا فقط اولین سیگنال را برمی‌گردانیم:
        signal, tf = signals[0]
        return (signal, symbol, tf)

    except Exception as e:
        print(f"❌ Error in strategy for {symbol}: {e}")
        return ("NONE", symbol, None)


def run_all_strategies_parallel():
    symbols = get_all_registered_symbols()
    print(f"🚀 Running strategy on {len(symbols)} symbols using {cpu_count()} cores...")

    buy_list = []
    sell_list = []
    no_signal_list = []

    with Pool(processes=cpu_count()) as pool:
        results = pool.map(run_strategy_for_symbol, symbols)

    for signal, symbol, tf in results:
        if signal == "BUY":
            buy_list.append((symbol, tf))
        elif signal == "SELL":
            sell_list.append((symbol, tf))
        else:
            no_signal_list.append((symbol, tf))

    print("\n==================== Strategy Summary ====================")
    print("🟢 Buy signals:", buy_list)
    print("🔴 Sell signals:", sell_list)
    print("⚪️ No signals:", no_signal_list)
    print("=========================================================")

    return buy_list, sell_list, no_signal_list
