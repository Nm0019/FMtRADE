from strategies.strategy_base import StrategyBase
from indicators.rsi import RSIIndicator
from indicators.macd import MACDIndicator

class CombinedRSIMACDStrategy(StrategyBase):

    def evaluate(self, df):
        rsi = RSIIndicator(self.symbol, self.timeframe, params={})
        macd = MACDIndicator(self.symbol, self.timeframe, params={})

        df = df.join(rsi.calculate(df))
        df = df.join(macd.calculate(df))

        last_row = df.iloc[-1]
        rsi_signal = last_row.get("signal_RSI", 0)
        macd_signal = last_row.get("signal_MACD", 0)

        if rsi_signal == macd_signal and rsi_signal != 0:
            return {
                "symbol": self.symbol,
                "timeframe": self.timeframe,
                "signal": rsi_signal,
                "confidence": "confirmed"
            }

        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "signal": 0,
            "confidence": "none"
        }

    def generate_signal(self, df):
        res = self.evaluate(df)
        signal = res.get("signal", 0)
        if signal == 1:
            return "BUY"
        elif signal == -1:
            return "SELL"
        else:
            return "NONE"
