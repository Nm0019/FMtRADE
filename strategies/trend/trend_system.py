# strategies/trend/trend_system.py

import pandas as pd
from database.db_operations import fetch_recent_data
from strategies.trend.ema_adx_strategy import EMAADXStrategy
# from strategies.trend.multi_ema_adx import MultiEMAADXStrategy
# from strategies.trend.mtf_rsi_vwap import MTFRSIVWAPStrategy
# from strategies.trend.gaussian_retracement import GaussianRetraceStrategy

class TrendSystem:
    def __init__(self, symbol: str, timeframe: str, config: dict = None):
        self.symbol = symbol
        self.timeframe = timeframe
        self.config = config or {}
        self.strategies = []

        self._initialize_strategies()

    def _initialize_strategies(self):
        """
        فعال‌سازی استراتژی‌ها با تنظیمات داینامیک.
        """
        self.strategies = [
            EMAADXStrategy(self.symbol, self.timeframe, self.config.get("ema_adx", {}))
            # MultiEMAADXStrategy(self.symbol, self.timeframe, self.config.get("multi_ema", {})),
            # MTFRSIVWAPStrategy(self.symbol, self.timeframe, self.config.get("mtf_rsi_vwap", {})),
            # GaussianRetraceStrategy(self.symbol, self.timeframe, self.config.get("gaussian", {})),
        ]

    def detect_trend(self, df: pd.DataFrame) -> dict:
        """
        اجرای تمام استراتژی‌ها بر اساس دیتای موجود
        """
        results = []
        for strat in self.strategies:
            result = strat.detect_trend(df)
            results.append(result)

        return self._combine_results(results)

    def detect_trend_from_db(self, limit=300) -> dict:
        """
        دریافت داده‌ها از دیتابیس و اجرای تحلیل
        """
        try:
            rows = fetch_recent_data(self.symbol, self.timeframe, limit=limit)
            df = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close", "volume"])
            df['time'] = pd.to_datetime(df['time'])

            return self.detect_trend(df)

        except Exception as e:
            return {
                "trend": "unknown",
                "score": 0,
                "details": [],
                "error": str(e)
            }

    def _combine_results(self, results: list) -> dict:
        """
        رأی‌گیری یا وزن‌دهی برای استخراج روند نهایی
        """
        trend_scores = {"up": 0, "down": 0, "sideways": 0}
        details = []

        for res in results:
            trend = res.get("trend", "unknown")
            score = res.get("confidence", 0)
            if trend in trend_scores:
                trend_scores[trend] += score
            details.append(res)
            print(f"{res['trend']} ({res['confidence']})")

        final_trend = max(trend_scores, key=trend_scores.get)
        
        return {
            "trend": final_trend,
            "score": trend_scores[final_trend],
            "details": details
        }

    @staticmethod
    def analyze_all(symbols: list, timeframes: list, config: dict = None) -> dict:
        """
        اجرای کامل سیستم برای تمام نمادها و تایم‌فریم‌ها
        خروجی: dict با کلید (symbol, timeframe)
        """
        result_map = {}

        for symbol in symbols:
            for tf in timeframes:
                try:
                    print(f"🔍 Running TrendSystem for {symbol} [{tf}]...")
                    ts = TrendSystem(symbol, tf, config)
                    result = ts.detect_trend_from_db()
                    result_map[(symbol, tf)] = result

                except Exception as e:
                    print(f"❌ Error in {symbol} [{tf}]: {e}")
                    result_map[(symbol, tf)] = {
                        "trend": "error",
                        "score": 0,
                        "details": [],
                        "error": str(e)
                    }

        return result_map
