import httpx

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
            raise Exception(f"Binance error: {r.text}")

        raw = r.json()

        candles = []
        for c in raw:
            candles.append({
                "time": int(float(c[0])) // 1000,
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
            })

        return candles
