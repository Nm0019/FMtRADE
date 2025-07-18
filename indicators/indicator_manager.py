import pandas as pd
import sqlite3

from indicators.rsi import RSIIndicator
from indicators.macd import MACDIndicator
from indicators.adx import ADXIndicator
from indicators.ema import EMAIndicator
from database.db_operations import fetch_recent_data, connect, get_table_name

def add_column_if_not_exists(conn: sqlite3.Connection, table: str, column: str):
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    if column not in columns:
        print(f"➕ Adding column '{column}' to {table}")
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} REAL")
        conn.commit()

def calculate_and_store_indicators(symbol: str, timeframe: str):
    print(f"📈 Calculating indicators for {symbol} [{timeframe}]...")
    table = get_table_name(timeframe)
    conn = connect(symbol)

    # دریافت داده‌ها از دیتابیس (limit 10000)
    df_rows = fetch_recent_data(symbol, timeframe, limit=10000 + 100)
    df = pd.DataFrame(df_rows, columns=["time", "open", "high", "low", "close", "volume"])
    if df.empty:
        print("⚠️ No data available.")
        conn.close()
        return

    # تعریف اندیکاتورها با نمونه کلاس و ستون‌های خروجی
    indicator_objects = [
        RSIIndicator(symbol, timeframe, params={
            "period": 14,
            "sma_short": 20,
            "sma_long": 50,
            "divergence_window": 20,
            "rsi_weight": 1,
            "trend_weight": 1,
            "divergence_weight": 1
        }),
        MACDIndicator(symbol, timeframe, params={"fast": 12, "slow": 26, "signal": 9}),
        ADXIndicator(symbol, timeframe, params={
            "period": 14,
            "ema_period": 50,
            "rsi_period": 14,
            "macd_fast": 12,
            "macd_slow": 26,
            "macd_signal": 9
        }),
        EMAIndicator(symbol, timeframe, params={"period": 50})
    ]

    # محاسبه اندیکاتورها یک‌بار و نگهداری نتایج
    cached_results = {}
    all_columns = set()

    for ind in indicator_objects:
        result = ind.calculate(df.copy())  # برای جلوگیری از آلودگی df
        cached_results[ind] = result
        all_columns.update([c for c in result.columns if c != "time"])

    # اضافه کردن ستون‌های خروجی به جدول دیتابیس
    for col in sorted(all_columns):
        add_column_if_not_exists(conn, table, col)

    # ادغام خروجی‌ها در df اصلی
    for result in cached_results.values():
        for col in result.columns:
            if col != "time":
                df[col] = result[col]

    # فرمت‌دهی زمان برای درج در دیتابیس
    df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # به‌روزرسانی مقادیر در دیتابیس
    cursor = conn.cursor()
    for idx, row in df.iterrows():
        time_val = row["time"]
        update_fields = []
        update_values = []

        for col in all_columns:
            val = row.get(col)
            if pd.notna(val):
                update_fields.append(f"{col} = ?")
                update_values.append(str(val))

        if update_fields:
            sql = f"UPDATE {table} SET {', '.join(update_fields)} WHERE time = ?"
            cursor.execute(sql, (*update_values, time_val))

    conn.commit()
    conn.close()
    print(f"✅ Indicators stored for {symbol} [{timeframe}]")