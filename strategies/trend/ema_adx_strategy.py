class EMAADXStrategy:
    def __init__(self, symbol: str, timeframe: str, config: dict):
        self.symbol = symbol
        self.timeframe = timeframe
        self.config = config or {}

        self.ema_period = self.config.get("ema", {}).get("period", 50)
        self.adx_period = self.config.get("adx", {}).get("period", 14)

    def detect_trend(self, df):
        df = df.copy()

        # === ستون‌های مورد نیاز
        required_cols = [
            f"ema_{self.ema_period}",
            "adx",
            "diplusn",
            "diminusn",
            "close"
        ]

        # بررسی وجود ستون‌ها
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            return {
                "trend": "unknown",
                "confidence": 0,
                "reason": f"Missing columns: {missing}"
            }

        # بررسی NaN
        df = df.dropna(subset=required_cols)
        if df.empty:
            return {
                "trend": "unknown",
                "confidence": 0,
                "reason": "No valid data after dropping NaNs"
            }

        # گرفتن آخرین ردیف معتبر
        latest = df.iloc[-1]
        adx = latest["adx"]
        diplus = latest["diplusn"]
        diminus = latest["diminusn"]
        ema = latest[f"ema_{self.ema_period}"]
        close = latest["close"]

        # === منطق تشخیص روند
        trend = "sideways"
        confidence = 0
        reasons = []

        if adx >= 25:
            if diplus > diminus and close > ema:
                trend = "up"
                confidence += 2
                reasons.append("DI+ > DI- و قیمت بالای EMA → روند صعودی")
            elif diminus > diplus and close < ema:
                trend = "down"
                confidence += 2
                reasons.append("DI- > DI+ و قیمت پایین EMA → روند نزولی")
            else:
                trend = "sideways"
                confidence += 1
                reasons.append("ADX بالا ولی EMA و DI تایید نمی‌کنند")
        else:
            reasons.append("ADX ضعیف → بازار بدون روند مشخص")

        return {
            "trend": trend,
            "confidence": confidence,
            "reason": " - ".join(reasons)
        }
