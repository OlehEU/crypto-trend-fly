import asyncio
'macd': {
'macd': macd_line,
'signal': macd_signal
}
}
return JSONResponse(resp)


# Forecast (as before)
@app.get('/api/forecast')
async def forecast(id: str = 'bitcoin', days: int = 30, lookback: int = 20, horizon: int = 6):
data = await fetch_market_chart(id, days)
prices = [p[1] for p in data]
pred = simple_forecast(prices, lookback=lookback, horizon=horizon)
return JSONResponse({'forecast': pred})


# Simple WebSocket manager to broadcast price updates
class ConnectionManager:
def __init__(self):
self.active_connections: dict[WebSocket, dict] = {}


async def connect(self, websocket: WebSocket, params: dict):
await websocket.accept()
self.active_connections[websocket] = params


def disconnect(self, websocket: WebSocket):
if websocket in self.active_connections:
del self.active_connections[websocket]


manager = ConnectionManager()


@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
# Client should send JSON message with {"symbol":"BTCUSDT","interval":"1m","update_secs":5}
await websocket.accept()
try:
msg = await websocket.receive_json()
symbol = msg.get('symbol', 'BTCUSDT')
interval = msg.get('interval', '1m')
update_secs = int(msg.get('update_secs', 5))
await manager.connect(websocket, {'symbol': symbol, 'interval': interval, 'update_secs': update_secs})
# push updates until disconnect
while True:
# fetch recent klines (1 latest)
data = await fetch_klines_binance(symbol, interval, limit=2)
if data:
k = data[-1]
payload = {
'time': int(k[0]//1000),
'open': float(k[1]),
'high': float(k[2]),
'low': float(k[3]),
'close': float(k[4])
}
await websocket.send_json({'type': 'kline', 'data': payload})
await asyncio.sleep(update_secs)
except WebSocketDisconnect:
manager.disconnect(websocket)
except Exception:
manager.disconnect(websocket)
try:
await websocket.close()
except:
pass
