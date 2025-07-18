# symbol_analysis.py

from indicators.indicator_runner import run_all_indicators_parallel
from strategies.trend.trend_runner import run_all_trend_strategies_parallel
# from strategies.filters.price_action_filter import apply_price_action_filter  # فرض بر این است که داریم
# from signal_center.signal_generator import generate_final_signals  # فایل نهایی تولید سیگنال
from config import TIMEFRAME_MAP


def run_all_symbols(symbols: list, timeframes: list, config: dict = None):
    print("\n🚀 Starting full analysis pipeline...")

    # 1. اجرای اندیکاتورها
    print("\n📈 Step 1: Calculating Indicators...")
    run_all_indicators_parallel()

    # 2. اجرای استراتژی‌ها
    print("\n🧠 Step 2: Running Trend Strategies...")
    trend_results = run_all_trend_strategies_parallel()
    print(trend_results)
    # 3. اعمال فیلتر پرایس اکشن (در صورت وجود)
    print("\n🔍 Step 3: Applying Price Action Filters...")
    filtered_results = []
    # for res in trend_results:
    #     if res["trend"] in ["up", "down"]:
    #         # passed = apply_price_action_filter(res["symbol"], res["timeframe"])
    #         if passed:
    #             res["passed_price_action"] = True
    #             filtered_results.append(res)
    #         else:
    #             res["passed_price_action"] = False

    # 4. تولید نهایی سیگنال
    print("\n📤 Step 4: Generating Final Signals...")
    # signals = generate_final_signals(filtered_results)

    # 5. گزارش نهایی
    # print("\n📊 Final Signals:")
    # for sig in signals:
    #     print(f"✅ {sig['symbol']} → {sig['action']} @ {sig['entry']} → Target: {sig['target']} | SL: {sig['stoploss']}")
    signals =0
    return signals
