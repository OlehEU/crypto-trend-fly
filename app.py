from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import time

from crypto_utils import (
    fetch_binance_klines,
    fetch_market_chart,
    calculate_indicators,
    simple_forecast
)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.get("/api/klines")
async def get_klines(symbol: str = "BTCUSDT", interval: str = "1m", limit: int = 200):
    data = await fetch_binance_klines(symbol, interval, limit)
    return JSONResponse(data)


@app.get("/api/market_chart")
async def get_market_chart(coin: str = "bitcoin", days: int = 1):
    data = await fetch_market_chart(coin, days)
    return JSONResponse(data)


@app.get("/api/indicators")
async def get_indicators(symbol: str = "BTCUSDT", interval: str = "1m", limit: int = 200):
    klines = await fetch_binance_klines(symbol, interval, limit)
    closes = [c["close"] for c in klines]
    result = calculate_indicators(closes)
    return result


@app.get("/api/forecast")
async def get_forecast(symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 200):
    klines = await fetch_binance_klines(symbol, interval, limit)
    closes = [c["close"] for c in klines]
    prediction = simple_forecast(closes)
    return {"forecast": prediction}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    while True:
        try:
            data = await fetch_binance_klines("BTCUSDT", "1m", 1)
            price = data[-1]["close"]

            await ws.send_text(json.dumps({"price": price, "time": time.time()}))
            await asyncio.sleep(2)
        except Exception as e:
            await ws.send_text(json.dumps({"error": str(e)}))
            await asyncio.sleep(5)
