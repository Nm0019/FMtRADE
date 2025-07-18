# from mt5_connector.historical_fetcher import (
#     connect_mt5,
#     shutdown_mt5,
#     get_crypto_symbols,
#     download_historical_data
# )
# from database.symbols_meta import register_symbol, get_all_registered_symbols
# from database.db_operations import initialize_symbol_db
# from indicators.indicator_manager import calculate_and_store_indicators
# from indicators.indicator_runner import run_all_indicators_parallel
# # from strategies.strategy_runner import run_all_strategies_parallel
# from config import SUPPORTED_TIMEFRAMES, TIMEFRAME_MAP


# def main():
#     # اتصال به MetaTrader 5
#     connect_mt5()

#     # گرفتن لیست نمادها
#     symbols = get_crypto_symbols()
#     print(f"🔍 Found {len(symbols)} crypto symbols")

#     # ثبت نمادها و ایجاد دیتابیس اختصاصی آنها
#     for symbol in symbols:
#         db_path = f"data/db_per_symbol/{symbol}.db"
#         register_symbol(symbol, db_path)
#         initialize_symbol_db(symbol, SUPPORTED_TIMEFRAMES)

#     # دریافت و ذخیره داده‌های تاریخی
#     download_historical_data(symbols)
#     print("✅ All historical data fetched.")

#     # محاسبه اندیکاتورها (موازی)
#     run_all_indicators_parallel()

#     # اجرای استراتژی (موازی) و دریافت لیست سیگنال‌ها
#     # buy_signals, sell_signals, no_signals = run_all_strategies_parallel()

#     # print("\n🔔 Final Signals:")
#     # print(f"🟢 Buy signals: {buy_signals}")
#     # print(f"🔴 Sell signals: {sell_signals}")
#     # print(f"⚪️ No signals: {no_signals}")

#     # قطع اتصال
#     shutdown_mt5()


# if __name__ == "__main__":
#     main()
