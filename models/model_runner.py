# models/model_runner.py
import pandas as pd
import traceback
from multiprocessing import Pool, cpu_count
from config import SUPPORTED_TIMEFRAMES, TIMEFRAME_MAP
from database.symbols_meta import get_all_registered_symbols
from database.db_operations import fetch_recent_data
from models.model_manager import save_model_result_to_db
from models.linear_models.linear_regr import linear_regression  # تابعی که مدل را اجرا می‌کند

def _run_for_symbol_and_tf(args):
    symbol, tf_enum = args
    tf_str = TIMEFRAME_MAP[tf_enum]

    try:
        print(f"📊 Running model for {symbol} [{tf_str}]")
        rows = fetch_recent_data(symbol, tf_str, limit=1200)
        df = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close", "volume"])

        if df.empty or len(df) < 100:
            print(f"⚠️ Not enough data for {symbol} [{tf_str}]")
            return

        result =linear_regression(df, symbol, tf_str)
        
        if result:
            save_model_result_to_db(symbol, tf_str,result)

    except Exception as e:
        print(f"❌ Error in model run for {symbol} [{tf_str}]: {e}")
        traceback.print_exc()


def run_all_models_parallel():
    symbols = get_all_registered_symbols()
    tasks = [(symbol, tf) for symbol in symbols for tf in SUPPORTED_TIMEFRAMES]

    print(f"🚀 Running {len(tasks)} ML jobs using {cpu_count()} cores...")
    with Pool(processes=cpu_count()) as pool:
        pool.map(_run_for_symbol_and_tf, tasks)

    print("✅ All ML model tasks completed.")
