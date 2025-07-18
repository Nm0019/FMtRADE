import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

def linear_regression(df, symbol, tf_str, forecast=2):
    df1 = df[['open', 'high', 'low', 'close']].copy()
    df1['Predict'] = df1['close'].shift(-forecast)
    df1.dropna(inplace=True)

    # ویژگی‌ها و هدف
    x = df1[['open', 'high', 'low', 'close']].values
    y = df1['Predict'].values

    # تقسیم داده‌ها
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, shuffle=False  # ترتیب زمانی حفظ شود
    )

    # مدل رگرسیون خطی
    model = LinearRegression()
    model.fit(x_train, y_train)

    # دقت مدل
    y_pred = model.predict(x_test)
    r_squared = r2_score(y_test, y_pred)

    # بررسی روند با پیش‌بینی‌های مرتب‌شده
    trend_slope = np.polyfit(np.arange(len(y_pred)), y_pred, 1)[0]
    direction = (
        "up" if trend_slope > 0 else
        "down" if trend_slope < 0 else
        "neutral"
    )

    # قدرت و سطح اطمینان
    strength = abs(trend_slope) * r_squared
    if r_squared >= 0.9:
        confidence = "very high"
    elif r_squared >= 0.75:
        confidence = "high"
    elif r_squared >= 0.5:
        confidence = "medium"
    else:
        confidence = "low"

    # پیش‌بینی آینده
    future_data = df1[['open', 'high', 'low', 'close']].values[-forecast:]
    forecast_prices = model.predict(future_data)

    return {
        "symbol": symbol,
        "timeframe": tf_str,
        "direction": direction,
        "slope": round(trend_slope, 6),
        "r_squared": round(r_squared, 4),
        "strength": round(strength, 4),
        "confidence": confidence,
        "forecast_prices": list(np.round(forecast_prices, 4)),
    }
