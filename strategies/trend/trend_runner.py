# strategies/trend/trend_runner.py

import pandas as pd
from database.db_operations import fetch_recent_data
from strategies.trend.trend_system import TrendSystem
from config import SUPPORTED_TIMEFRAMES, TIMEFRAME_MAP

def run_trend_analysis_for_symbol(symbol: str, tf_enum, config: dict = None):
    tf_str = TIMEFRAME_MAP[tf_enum]  # تبدیل enum به رشته مانند "m5"

    # دریافت داده از دیتابیس
    rows = fetch_recent_data(symbol, tf_str, limit=500)
    df = rows  # fetch_recent_data دیتافریم کامل است


    if df.empty:
        return {"symbol": symbol, "timeframe": tf_str, "trend": "unknown", "score": 0, "reason": "No data"}

    # اجرای سیستم تشخیص روند
    trend_system = TrendSystem(symbol, tf_str, config)
    result = trend_system.detect_trend(df)
    print("📊 Columns in df:", df.columns.tolist())
    print(df.tail(3))
    print("📋 All columns in df:", df.columns.tolist())
    print(df.tail(1).T)


    # print(f"🧪 [{symbol}] {tf_str}: Last ADX={df['adx'].iloc[-1]}, EMA={df[f'ema_50'].iloc[-1]}, Close={df['close'].iloc[-1]}")


    return {
        "symbol": symbol,
        "timeframe": tf_str,
        "trend": result["trend"],
        "score": result["score"],
        "details": result["details"]
    }

# strategies/strategy_runner.py

def run_all_trend_strategies_parallel():
    from multiprocessing import Pool
    from config import SUPPORTED_TIMEFRAMES
    from mt5_connector.historical_fetcher import get_crypto_symbols
    from strategies.trend.trend_runner import run_trend_analysis_for_symbol

    symbols = get_crypto_symbols()
    tasks = []

    for symbol in symbols:
        for tf in SUPPORTED_TIMEFRAMES:
            tasks.append((symbol, tf))

    with Pool() as pool:
        results = pool.starmap(run_trend_analysis_for_symbol, tasks)

    return results
