import httpx
import numpy as np


async def fetch_binance_klines(symbol="BTCUSDT", interval="1m", limit=200):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        raw = r.json()

    candles = []
    for c in raw:
        candles.append({
            "time": c[0] // 1000,
            "open": float(c[1]),
            "high": float(c[2]),
            "low": float(c[3]),
            "close": float(c[4]),
            "volume": float(c[5]),
        })
    return candles


async def fetch_market_chart(coin="bitcoin", days=1):
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days={days}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return r.json()


def ema(values, period):
    arr = np.array(values, dtype=float)
    return list(np.round(pd.Series(arr).ewm(span=period).mean(), 2))


def rsi(values, length=14):
    values = np.array(values, dtype=float)
    diff = np.diff(values)
    up = diff.clip(min=0)
    down = (-diff.clip(max=0))

    roll_up = np.mean(up[:length])
    roll_down = np.mean(down[:length])

    rsi_values = []
    for i in range(length, len(values) - 1):
        roll_up = (roll_up * (length - 1) + up[i]) / length
        roll_down = (roll_down * (length - 1) + down[i]) / length

        rs = roll_up / roll_down if roll_down != 0 else 0
        rsi_values.append(100 - (100 / (1 + rs)))

    return rsi_values


def macd(values):
    arr = np.array(values, float)
    ema12 = pd.Series(arr).ewm(span=12).mean()
    ema26 = pd.Series(arr).ewm(span=26).mean()
    macd_line = ema12 - ema26
    signal = macd_line.ewm(span=9).mean()
    hist = macd_line - signal

    return {
        "macd": list(macd_line),
        "signal": list(signal),
        "hist": list(hist)
    }


def calculate_indicators(closes):
    return {
        "ema20": ema(closes, 20),
        "ema50": ema(closes, 50),
        "rsi": rsi(closes),
        "macd": macd(closes)
    }


def simple_forecast(closes):
    arr = np.array(closes)
    slope = (arr[-1] - arr[-20]) / 20
    return float(arr[-1] + slope * 10)
