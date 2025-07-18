# strategies/signal_strategy_executor.py


import pandas as pd
from database.db_operations import fetch_recent_data
from indicators.indicator_manager import calculate_and_store_indicators
from strategies.trend_analysis import TrendAnalyzer
from strategies.price_action import PriceActionAnalyzer
from strategies.signal_combiner import SignalCombiner
from strategies.json_generator import SignalJsonBuilder

class SignalStrategyExecutor:
    def __init__(self, symbol: str, timeframe: str):
        self.symbol = symbol
        self.timeframe = timeframe
        self.df = None
        self.context = {}

    def load_data(self):
        rows = fetch_recent_data(self.symbol, self.timeframe, limit=1000)
        self.df = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close", "volume"])
        self.df['time'] = pd.to_datetime(self.df['time'])


    def run_indicators(self):
        calculate_and_store_indicators(self.symbol, self.timeframe)
        # مجدداً دریافت دیتا با خروجی اندیکاتورها
        rows = fetch_recent_data(self.symbol, self.timeframe, limit=1000)
        self.df = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close", "volume"])  # اندیکاتورها ضمیمه شده‌اند
        self.df['time'] = pd.to_datetime(self.df['time'])

    
    def analyze_trend(self):
        trend = TrendAnalyzer.analyze(self.symbol)
        self.context['trend'] = trend

    def analyze_price_action(self):
        pa_result = PriceActionAnalyzer.analyze(self.df, self.timeframe)
        self.context['price_action'] = pa_result

    def combine_conditions(self):
        combiner = SignalCombiner()
        signal, score, reasons = combiner.combine(self.df, self.context)
        self.context['signal'] = signal
        self.context['score'] = score
        self.context['reasons'] = reasons

    def generate_signal_json(self):
        builder = SignalJsonBuilder()
        return builder.build(self.symbol, self.timeframe, self.df, self.context)

    def run(self):
        self.load_data()
        self.run_indicators()
        self.analyze_trend()
        self.analyze_price_action()
        self.combine_conditions()
        return self.generate_signal_json()



    