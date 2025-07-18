# controller.py

import time
from mt5_connector.historical_fetcher import (
    connect_mt5,
    shutdown_mt5,
    get_crypto_symbols,
    download_historical_data
)
from database.symbols_meta import register_symbol
from database.db_operations import initialize_symbol_db
from symbol_analysis import run_all_symbols  # 🔁 نام تابع اصلی تحلیل
from config import SUPPORTED_TIMEFRAMES
from command_center.server_client import SignalClient


def prepare_environment():
    # اتصال به MT5
    connect_mt5()
    print("🔗 Connected to MetaTrader 5")

    symbols = get_crypto_symbols()
    print(f"🔍 Found {len(symbols)} crypto symbols")

    # ثبت و آماده‌سازی دیتابیس‌ها
    for symbol in symbols:
        db_path = f"data/db_per_symbol/{symbol}.db"
        register_symbol(symbol, db_path)
        initialize_symbol_db(symbol, SUPPORTED_TIMEFRAMES)

    # دانلود داده‌های تاریخی
    download_historical_data(symbols)
    print("✅ Historical data updated.")
    return symbols


def run_cycle(client: SignalClient):
    try:
        symbols = prepare_environment()

        # اجرای تحلیل کامل برای هر نماد
        run_all_symbols(symbols, SUPPORTED_TIMEFRAMES)

    except Exception as e:
        print(f"❌ Error in run_cycle: {e}")

    finally:
        shutdown_mt5()
        print("🔌 MetaTrader disconnected.")


def main():
    client = SignalClient()
    client.connect()

    try:
        while True:
            print("\n⏳ Starting new signal generation cycle...")
            run_cycle(client)
            print("✅ Cycle completed. Waiting 60 seconds before next cycle...\n")
            time.sleep(60)

    except KeyboardInterrupt:
        print("🛑 Stopping system by user...")

    finally:
        client.send_exit()
        client.close()


if __name__ == "__main__":
    main()
