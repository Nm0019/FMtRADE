import sqlite3

def add_column_if_not_exists(conn: sqlite3.Connection, table: str, column: str, col_type: str):
    """بررسی و افزودن ستون به جدول در صورت عدم وجود"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    if column not in columns:
        print(f"➕ Adding column '{column}' to {table}")
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        conn.commit()

def save_model_result_to_db(symbol: str, timeframe: str, result: dict):
    """ذخیره خروجی مدل در همه ردیف‌های جدول دیتابیس مربوط به نماد و تایم‌فریم"""
    db_path = f"data/db_per_symbol/{symbol}.db"
    table_name = f"ohlcv_{timeframe}"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ستون‌های مورد نیاز مدل
    columns = {
        "direction": "TEXT",
        "slope": "REAL",
        "r_squared": "REAL",
        "confidence": "TEXT",
        "strength": "REAL",
        "forecast_prices": "REAL"
    }

    # بررسی و ایجاد ستون‌ها در صورت نبودن
    for col, col_type in columns.items():
        add_column_if_not_exists(conn, table_name, col, col_type)

    # به‌روزرسانی همه ردیف‌ها
    update_query = f"""
        UPDATE {table_name}
        SET direction = ?,
            slope = ?,
            r_squared = ?,
            confidence = ?,
            strength = ?
    """
    cursor.execute(update_query, (
        result.get("direction"),
        result.get("slope"),
        result.get("r_squared"),
        result.get("confidence"),
        result.get("strength"),
    ))

    conn.commit()
    conn.close()
    print(f"📥 Model results saved to all rows in {symbol}.db [{timeframe}]")
