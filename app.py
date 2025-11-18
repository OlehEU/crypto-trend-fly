from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import httpx

app = FastAPI(title="Crypto Trend Web")

# Статика
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# API route для получения данных по монете
@app.get("/api/coin/{coin_id}")
async def get_coin_data(coin_id: str, days: int = 1):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return JSONResponse(content=data)
        except httpx.HTTPStatusError:
            return JSONResponse(content={"error": "Не удалось получить данные"}, status_code=400)

# API для поиска монеты по названию/ID
@app.get("/api/search")
async def search_coin(query: str):
    url = f"https://api.coingecko.com/api/v3/search"
    params = {"query": query}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return JSONResponse(content=data)
        except httpx.HTTPStatusError:
            return JSONResponse(content={"error": "Не удалось выполнить поиск"}, status_code=400)
