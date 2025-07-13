# ✅ AI Signal Bot with HTF+LTF, SL/TP, Trailing Stop, Volatility Filter (Render-ready)

import ccxt
import pandas as pd
import pandas_ta as ta
import requests
import time

# === CONFIG ===
TELEGRAM_TOKEN = "7936186728:AAGq3_O-T0MSyyYmDZ7AUDza8EZi83rFkI4"
TELEGRAM_CHAT_ID = "6684603246"
SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT",
    "DOGE/USDT", "ADA/USDT", "AVAX/USDT", "DOT/USDT", "MATIC/USDT",
    "SHIB/USDT", "LTC/USDT", "TRX/USDT", "LINK/USDT", "NEAR/USDT",
    "ATOM/USDT", "OP/USDT", "ARB/USDT", "INJ/USDT", "RNDR/USDT",
    "AAVE/USDT", "GRT/USDT", "SAND/USDT", "MANA/USDT", "AXS/USDT",
    "FLOW/USDT", "IMX/USDT", "DYDX/USDT", "PEPE/USDT", "STX/USDT",
    "FTM/USDT", "TWT/USDT", "CRV/USDT", "LDO/USDT", "COMP/USDT",
    "COTI/USDT", "KAVA/USDT", "CAKE/USDT", "ALGO/USDT", "CHZ/USDT",
    "GALA/USDT", "RUNE/USDT", "1000FLOKI/USDT", "1000SATS/USDT", "1000BONK/USDT"
]
LTF = "15m"  # Entry timeframe
HTF = "4h"    # Trend timeframe
ATR_LEN = 14
RISK_MULTIPLIER = 1.5  # for SL, TP
MIN_CONFIDENCE = 3

# === FUNCTIONS ===
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=payload)

def fetch_ohlcv(symbol, timeframe, limit=100):
    exchange = ccxt.binance()
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

def add_indicators(df):
    df.ta.ema(length=20, append=True)
    df.ta.ema(length=50, append=True)
    df.ta.rsi(length=14, append=True)
    df.ta.macd(append=True)
    df.ta.atr(length=ATR_LEN, append=True)
    return df

def is_trending_up(df):
    latest = df.iloc[-1]
    return latest["EMA_20"] > latest["EMA_50"] and latest["MACDh_12_26_9"] > 0

def is_trending_down(df):
    latest = df.iloc[-1]
    return latest["EMA_20"] < latest["EMA_50"] and latest["MACDh_12_26_9"] < 0

def volatility_ok(df):
    atr = df["ATR_14"].iloc[-1]
    body = abs(df["close"].iloc[-1] - df["open"].iloc[-1])
    return body >= 0.4 * atr  # avoid chop

def analyze_pair(symbol):
    try:
        df_htf = add_indicators(fetch_ohlcv(symbol, HTF))
        df_ltf = add_indicators(fetch_ohlcv(symbol, LTF))
        trend_up = is_trending_up(df_htf)
        trend_down = is_trending_down(df_htf)
        if not volatility_ok(df_ltf):
            return None  # Skip if not volatile

        latest = df_ltf.iloc[-1]
        score = 0
        if trend_up and latest["EMA_20"] > latest["EMA_50"]: score += 1
        if trend_down and latest["EMA_20"] < latest["EMA_50"]: score += 1
        if latest["RSI_14"] > 55 or latest["RSI_14"] < 45: score += 1
        if (trend_up and latest["MACDh_12_26_9"] > 0) or (trend_down and latest["MACDh_12_26_9"] < 0): score += 1

        if score < MIN_CONFIDENCE:
            return None

        atr = latest["ATR_14"]
        price = latest["close"]
        direction = "BUY" if trend_up else "SELL"

        if direction == "BUY":
            sl = price - RISK_MULTIPLIER * atr
            tp = price + RISK_MULTIPLIER * atr
            trail = price - 0.5 * atr
        else:
            sl = price + RISK_MULTIPLIER * atr
            tp = price - RISK_MULTIPLIER * atr
            trail = price + 0.5 * atr

        return f"{symbol} | {direction} \nPrice: {price:.2f}\nSL: {sl:.2f}\nTP: {tp:.2f}\nTrail: {trail:.2f}\nScore: {score}/4"

    except Exception as e:
        return f"⚠️ Error on {symbol}: {e}"

def main():
    results = []
    for symbol in SYMBOLS:
        result = analyze_pair(symbol)
        if result:
            results.append(result)

    if results:
        msg = f"📈 AI Pro Signals ({datetime.now().strftime('%H:%M')}):\n\n" + "\n\n".join(results)
        send_telegram(msg)
    else:
        print("No valid trades.")

if __name__ == "__main__":
    main()
