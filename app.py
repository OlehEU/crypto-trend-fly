# app.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio

app = FastAPI()

# Разрешаем CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можно указать конкретный домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтируем папку static на корень
app.mount("/", StaticFiles(directory="static", html=True), name="static")

BINANCE_API_BASE = "https://api.binance.com/api/v3/klines"

async def fetch_binance_klines(symbol: str, interval: str, limit: int = 100):
    params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
    async with httpx.AsyncClient() as client:
        response = await client.get(BINANCE_API_BASE, params=params)
        response.raise_for_status()
        raw_data = response.json()
        # Преобразуем данные в читаемый формат
        klines = [
            {
                "time": int(c[0]) // 1000,  # Время в секундах
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
                "volume": float(c[5])
            }
            for c in raw_data
        ]
        return klines

# API для фронтенда
@app.get("/api/klines")
async def get_klines(symbol: str, interval: str, limit: int = 100):
    try:
        data = await fetch_binance_klines(symbol, interval, limit)
        return data
    except Exception as e:
        return {"error": str(e)}
