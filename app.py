from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from cachetools import TTLCache
import httpx
from statistics import mean

app = FastAPI(title="Crypto Trend API")

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Кэш: 5 минут
cache = TTLCache(maxsize=100, ttl=300)

COINGECKO_API = "https://api.coingecko.com/api/v3"

def ema(values, period):
    k = 2 / (period + 1)
    ema_arr = [values[0]]
    for v in values[1:]:
        ema_arr.append(v * k + ema_arr[-1] * (1 - k))
    return ema_arr

@app.get("/api/coin/{coin_id}")
async def get_coin_data(coin_id: str, days: int = 1):
    cache_key = f"{coin_id}_{days}"
    if cache_key in cache:
        return cache[cache_key]

    url = f"{COINGECKO_API}/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="CoinGecko API error")
        data = resp.json()

    prices = data.get("prices")
    if not prices:
        raise HTTPException(status_code=404, detail="No price data found")

    closes = [p[1] for p in prices]
    ema20 = ema(closes, 20)
    ema50 = ema(closes, 50)

    last_price = closes[-1]
    last_ema20 = ema20[-1]
    last_ema50 = ema50[-1]
    trend = "Восходящий ▲" if last_ema20 > last_ema50 else "Нисходящий ▼"
    strength_pct = abs((last_ema20 - last_ema50) / last_ema50) * 100
    if strength_pct < 0.3:
        strength = "Слабый"
    elif strength_pct < 1:
        strength = "Средний"
    else:
        strength = "Сильный"

    result = {
        "coin": coin_id,
        "last_price": last_price,
        "trend": trend,
        "strength": f"{strength} ({strength_pct:.2f}%)",
        "prices": [{"time": int(p[0]/1000), "value": p[1]} for p in prices],
        "ema20": [{"time": int(p[0]/1000), "value": v} for p,v in zip(prices, ema20)],
        "ema50": [{"time": int(p[0]/1000), "value": v} for p,v in zip(prices, ema50)]
    }

    cache[cache_key] = result
    return result

@app.get("/health")
async def health():
    return {"status": "ok"}
