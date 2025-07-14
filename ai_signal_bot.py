✅ Crypto Signal Bot for Binance Futures (15m Scalping, 40 Pairs, Telegram Alerts Only, Confidence Scoring)

import ccxt import pandas as pd import pandas_ta as ta import time import requests from datetime import datetime

=== CONFIGURATION ===

TELEGRAM_TOKEN = '7936186728:AAGq3_O-T0MSyyYmDZ7AUDza8EZi83rFkI4' CHAT_ID = '6684603246' TIMEFRAME = '15m' LIMIT = 150

=== 40 Binance Futures Pairs (You can modify this list) ===

symbols = [ 'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT', 'DOGE/USDT', 'AVAX/USDT', 'DOT/USDT', 'MATIC/USDT', 'LTC/USDT', 'BCH/USDT', 'UNI/USDT', 'LINK/USDT', 'ATOM/USDT', 'FIL/USDT', 'ETC/USDT', 'NEAR/USDT', 'OP/USDT', 'APE/USDT', 'SAND/USDT', 'MANA/USDT', 'AAVE/USDT', 'AR/USDT', 'XTZ/USDT', 'RNDR/USDT', 'GALA/USDT', 'DYDX/USDT', '1000PEPE/USDT', '1000SHIB/USDT', 'BLUR/USDT', 'WOO/USDT', 'XLM/USDT', 'TRX/USDT', 'IMX/USDT', 'RUNE/USDT', 'COTI/USDT', 'LDO/USDT', 'FET/USDT', 'INJ/USDT' ]

exchange = ccxt.binance({"enableRateLimit": True}) exchange.set_sandbox_mode(False)

=== Send Telegram Message ===

def send_telegram(message): url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage" payload = {"chat_id": CHAT_ID, "text": message} requests.post(url, data=payload)

=== Analyze Market ===

def analyze_symbol(symbol): try: ohlcv = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=LIMIT) df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']) df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Add indicators
    df.ta.ema(length=9, append=True)
    df.ta.ema(length=21, append=True)
    df.ta.ema(length=50, append=True)
    df.ta.rsi(length=14, append=True)
    df.ta.macd(append=True)
    df.ta.stoch(append=True)
    df.ta.cci(append=True)
    df.ta.atr(length=14, append=True)
    df.ta.bbands(append=True)
    df.ta.adx(append=True)

    latest = df.iloc[-1]

    # Confidence scoring system
    score = 0
    total = 4

    # Buy signal components
    if latest['RSI_14'] < 30:
        score += 1
    if latest['MACDh_12_26_9'] > 0:
        score += 1
    if latest['close'] > latest['EMA_21']:
        score += 1
    if latest['STOCHk_14_3_3'] < 20:
        score += 1

    confidence = int((score / total) * 100)

    if confidence >= 75:
        msg = f"\ud83d\ude80 BUY Signal\nSymbol: {symbol}\nTimeframe: {TIMEFRAME}\nPrice: {latest['close']:.2f}\nIndicators: RSI<30, MACD bullish, Price>EMA21, StochK<20\nConfidence: {confidence}%"
        send_telegram(msg)

    # Sell signal components
    score = 0
    if latest['RSI_14'] > 70:
        score += 1
    if latest['MACDh_12_26_9'] < 0:
        score += 1
    if latest['close'] < latest['EMA_21']:
        score += 1
    if latest['STOCHk_14_3_3'] > 80:
        score += 1

    confidence = int((score / total) * 100)

    if confidence >= 75:
        msg = f"\ud83d\udd25 SELL Signal\nSymbol: {symbol}\nTimeframe: {TIMEFRAME}\nPrice: {latest['close']:.2f}\nIndicators: RSI>70, MACD bearish, Price<EMA21, StochK>80\nConfidence: {confidence}%"
        send_telegram(msg)

except Exception as e:
    print(f"Error for {symbol}: {e}")

=== Main Loop ===

def run(): for symbol in symbols: market = symbol.replace("/", ":") analyze_symbol(market) time.sleep(1.2)  # Respect rate limit

if name == "main": run()

