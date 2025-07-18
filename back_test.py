import pandas as pd
from indicators.rsi import RSIIndicator
from indicators.macd import MACDIndicator
from database.db_operations import fetch_recent_data
from mt5_connector.historical_fetcher import get_crypto_symbols, connect_mt5, shutdown_mt5
from config import SUPPORTED_TIMEFRAMES, TIMEFRAME_MAP

def run_combined_backtest():
    print("📊 Starting Combined RSI + MACD Backtest...\n")
    connect_mt5()

    INITIAL_BALANCE = 200
    LOT_SIZE = 0.01
    LEVERAGE = 10
    SPREAD_COST = 1
    PIP_VALUE = 0.0001

    STOP_LOSS_PIPS = 6000 * PIP_VALUE
    TAKE_PROFIT_PIPS = 5000 * PIP_VALUE
    TRAIL_TRIGGER = 6000 * PIP_VALUE

    stats = []

    try:
        symbols = get_crypto_symbols()
        if not symbols:
            print("⚠️ No symbols found.")
            return

        for symbol in symbols:
            for tf in SUPPORTED_TIMEFRAMES:
                tf_str = TIMEFRAME_MAP.get(tf, str(tf))

                try:
                    df_rows = fetch_recent_data(symbol, tf_str, limit=1000)
                    df = pd.DataFrame(df_rows, columns=["time", "open", "high", "low", "close", "volume"])
                except Exception as e:
                    print(f"⚠️ Skip {symbol} [{tf_str}]: {e}")
                    continue

                if df.empty:
                    print(f"⏭️ No data for {symbol} [{tf_str}]")
                    continue

                # ⬇️ اجرای هر دو اندیکاتور
                rsi = RSIIndicator(symbol, tf_str, params={})
                macd = MACDIndicator(symbol, tf_str, params={})

                df = df.join(rsi.calculate(df))
                df = df.join(macd.calculate(df))

                balance = INITIAL_BALANCE
                total_exposure = 0
                win_count = 0
                loss_count = 0
                max_consec_losses = 0
                current_losses = 0
                trades = 0

                i = 3
                while i < len(df):
                    row = df.iloc[i]
                    prev_signals = df["signal_RSI"].iloc[i-3:i].values

                    if all(p == 0 for p in prev_signals):
                        rsi_sig = row.get("signal_RSI", 0)
                        macd_sig = row.get("signal_MACD", 0)

                        # 📌 شرط سیگنال مشترک:
                        if rsi_sig == macd_sig and rsi_sig != 0:
                            signal = rsi_sig
                        else:
                            signal = 0

                        if signal == 0:
                            i += 1
                            continue

                        entry_price = row["close"]
                        direction = "buy" if signal == 1 else "sell"
                        sl = entry_price - STOP_LOSS_PIPS if direction == "buy" else entry_price + STOP_LOSS_PIPS
                        tp = entry_price + TAKE_PROFIT_PIPS if direction == "buy" else entry_price - TAKE_PROFIT_PIPS

                        trailing_active = False
                        best_price = entry_price

                        j = i + 1
                        while j < len(df):
                            current_price = df["close"].iloc[j]

                            if direction == "buy":
                                if current_price - entry_price > TRAIL_TRIGGER:
                                    trailing_active = True
                                    best_price = max(best_price, current_price)
                                    sl = max(sl, best_price - STOP_LOSS_PIPS)
                                if current_price <= sl or current_price >= tp:
                                    break
                            else:
                                if entry_price - current_price > TRAIL_TRIGGER:
                                    trailing_active = True
                                    best_price = min(best_price, current_price)
                                    sl = min(sl, best_price + STOP_LOSS_PIPS)
                                if current_price >= sl or current_price <= tp:
                                    break
                            j += 1

                        exit_price = df["close"].iloc[j] if j < len(df) else df["close"].iloc[-1]
                        pl = (exit_price - entry_price) * 100 if direction == "buy" else (entry_price - exit_price) * 100
                        profit = pl * LOT_SIZE - SPREAD_COST
                        exposure = (entry_price * LOT_SIZE) / LEVERAGE

                        balance += profit
                        total_exposure += exposure
                        trades += 1

                        if profit > 0:
                            win_count += 1
                            current_losses = 0
                        else:
                            loss_count += 1
                            current_losses += 1
                            max_consec_losses = max(max_consec_losses, current_losses)

                        i = j
                    else:
                        i += 1

                win_rate = (win_count / trades) * 100 if trades > 0 else 0
                stats.append((symbol, tf_str, trades, win_rate, max_consec_losses, round(total_exposure, 2), round(balance, 2)))
                print(f"✅ {symbol} [{tf_str}] ➤ Trades: {trades} | WinRate: {win_rate:.1f}% | MaxLosses: {max_consec_losses} | Final: ${balance:.2f}")

        print("\n📈 Final Summary:")
        for s, tf, trades, win_rate, max_losses, exposure, final_balance in stats:
            print(f"{s:10} [{tf:3}] ➤ Trades: {trades:3} | WinRate: {win_rate:5.1f}% | MaxLosses: {max_losses:2} | Exposure: ${exposure:8.2f} | Final: ${final_balance:8.2f}")

        total_final = sum(row[-1] for row in stats)
        total_exposure = sum(row[-2] for row in stats)
        total_initial = INITIAL_BALANCE * len(stats)
        total_profit = total_final - total_initial
        profit_percent = (total_profit / total_initial) * 100 if total_initial > 0 else 0

        print("\n💰 Total Portfolio Performance:")
        print(f"Initial Capital : ${total_initial:,.2f}")
        print(f"Final Capital   : ${total_final:,.2f}")
        print(f"Total Exposure  : ${total_exposure:,.2f}")
        print(f"Total Profit    : ${total_profit:,.2f} ({profit_percent:.2f}%)")

    finally:
        shutdown_mt5()
        print("\n🏁 Backtest simulation completed.")


if __name__ == "__main__":
    run_combined_backtest()
