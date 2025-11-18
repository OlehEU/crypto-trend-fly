from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


BINANCE_API = "https://api.binance.com/api/v3/klines"


async def fetch_binance_klines(symbol: str, interval: str, limit: int):
    url = f"{BINANCE_API}?symbol={symbol}&interval={interval}&limit={limit}"

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; FlyIO/1.0)",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(headers=headers, timeout=10) as client:
        r = await client.get(url)

        if r.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Binance error: {r.text}"
            )

        raw = r.json()

        candles = []
        for c in raw:
            candles.append({
                "time": int(c[0] / 1000),
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
            })

        return candles


@app.get("/api/klines")
async def get_klines(symbol: str = "BTCUSDT", interval: str = "1m", limit: int = 50):
    try:
        return await fetch_binance_klines(symbol, interval, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
