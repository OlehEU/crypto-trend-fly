import httpx
import datetime

API_URL = "https://api.coingecko.com/api/v3"

async def get_price_history(symbol="bitcoin", days=30):
    url = f"{API_URL}/coins/{symbol}/market_chart?vs_currency=usd&days={days}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()
        prices = data["prices"]  # [timestamp, price]
        return [(datetime.datetime.fromtimestamp(p[0]/1000), p[1]) for p in prices]

def get_trend(prices):
    if len(prices) < 2:
        return "unknown"
    return "up" if prices[-1][1] > prices[0][1] else "down"
