from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import httpx
import statistics

app = FastAPI()
app.mount("/", StaticFiles(directory="static", html=True), name="static")

COINGECKO_API = "https://api.coingecko.com/api/v3"

def ema(values, period):
    """Compute EMA."""
    k = 2 / (period + 1)
    ema_list = [values[0]]
    for v in values[1:]:
        ema_list.append(v * k + ema_list[-1] * (1 - k))
    return ema_list

@app.get("/api/coin/{coin_id}")
async def get_coin_data(coin_id: str, days: int = 1):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{COINGECKO_API}/coins/{coin_id}/market_chart",
                               params={"vs_currency":"usd","days":days})
        if res.status_code != 200:
            return JSONResponse(status_code=404, content={"error":"Coin not found"})
        data = res.json()

    prices_raw = data["prices"]
    prices = [{"time": int(p[0]/1000), "value": p[1]} for p in prices_raw]
    close_prices = [p[1] for p in prices_raw]

    ema20_vals = ema(close_prices, 20)
    ema50_vals = ema(close_prices, 50)

    ema20 = [{"time": int(prices_raw[i][0]/1000), "value": ema20_vals[i]} for i in range(len(prices_raw))]
    ema50 = [{"time": int(prices_raw[i][0]/1000), "value": ema50_vals[i]} for i in range(len(prices_raw))]

    last_price = close_prices[-1]
    trend = "Восходящий ▲" if ema20_vals[-1] > ema50_vals[-1] else "Нисходящий ▼"
    pct = abs((ema20_vals[-1]-ema50_vals[-1])/ema50_vals[-1])*100
    strength = "Слабый" if pct < 0.3 else "Средний" if pct < 1 else "Сильный"

    return {
        "prices": prices,
        "ema20": ema20,
        "ema50": ema50,
        "last_price": last_price,
        "trend": trend,
        "strength": f"{strength} ({pct:.2f}%)"
    }
