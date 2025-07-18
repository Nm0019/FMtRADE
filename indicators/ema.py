# indicators/ema_indicator.py

import pandas as pd
from .base_indicator import BaseIndicator

class EMAIndicator(BaseIndicator):
    """
    EMA Indicator
    """

    def __init__(self, symbol, timeframe, params):
        super().__init__(symbol, timeframe, params)
        self.period = params.get("period", 14)

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        if 'close' not in df.columns:
            raise ValueError("DataFrame must contain 'close' column")

        df[f"ema_{self.period}"] = df['close'].ewm(span=self.period, adjust=False).mean()

        # تعریف شرط ساده سیگنال:
        def make_signal(row):
            if row['close'] > row[f"ema_{self.period}"]:
                return 'Buy'
            elif row['close'] < row[f"ema_{self.period}"]:
                return 'Sell'
            return 'Hold'

        df['sig_ema'] = df.apply(make_signal, axis=1)

        return df[['time', f"ema_{self.period}", 'sig_ema']]
    def get_ema_series(self, df: pd.DataFrame) -> pd.Series:
        return df['close'].ewm(span=self.period, adjust=False).mean()

    def get_ema_signal(self, df: pd.DataFrame) -> pd.Series:
        ema = self.get_ema_series(df)
        signal = df['close'].gt(ema).replace({True: 'Buy', False: 'Sell'})
        return signal.rename('sig_ema')
