import MetaTrader5 as mt5
import pandas as pd
from database.db_operations import insert_ohlcv_data, initialize_symbol_db
from config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER, HIST_CANDLES, SUPPORTED_TIMEFRAMES
from database.symbols_meta import register_symbol
from database.db_operations import get_db_path


# نگاشت ENUM های متاتریدر به رشته‌های خوانا برای دیتابیس
TIMEFRAME_MAP = {
    mt5.TIMEFRAME_M1: 'M1',
    mt5.TIMEFRAME_M5: 'M5',
    mt5.TIMEFRAME_M15: 'M15',
    mt5.TIMEFRAME_M30: 'M30',
    mt5.TIMEFRAME_H1: 'H1',
    mt5.TIMEFRAME_H4: 'H4',
}

def connect_mt5():
    if not mt5.initialize(login=MT5_LOGIN, server=MT5_SERVER, password=MT5_PASSWORD):
        raise RuntimeError(f"MT5 connection failed: {mt5.last_error()}")
    print("✅ Connected to MetaTrader 5")

def get_crypto_symbols():
    symbols = mt5.symbols_get()
    return [s.name for s in symbols if s.path and 'crypto' in s.path.lower()]

def download_historical_data(symbols):
    for symbol in symbols:
        # اطمینان از ساخت دیتابیس و جداول
        initialize_symbol_db(symbol)
        
        # ثبت نماد در دیتابیس مرکزی
        db_path = get_db_path(symbol)
        register_symbol(symbol, db_path)


        for timeframe in SUPPORTED_TIMEFRAMES:
            tf_str = TIMEFRAME_MAP.get(timeframe, str(timeframe))
            print(f"📥 Fetching {HIST_CANDLES} candles for {symbol} [{tf_str}]...")

            if not mt5.symbol_select(symbol, True):
                print(f"❌ Cannot select symbol: {symbol}")
                continue

            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, HIST_CANDLES)

            if rates is None or len(rates) == 0:
                print(f"⚠️ No data for {symbol} [{tf_str}]")
                continue

            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
            print(df.head())
            print(f"Inserting {len(df)} rows for {symbol} [{tf_str}]")

            insert_ohlcv_data(df, symbol, tf_str)

    print("✅ All historical data fetched.")

def shutdown_mt5():
    mt5.shutdown()
    print("🛑 MT5 connection closed")
