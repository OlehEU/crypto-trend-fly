import httpx
return []
k = 2 / (period + 1)
ema = []
prev = prices[0]
ema.append(prev)
for p in prices[1:]:
prev = p * k + prev * (1 - k)
ema.append(prev)
return ema


# RSI
def calc_rsi(prices, period=14):
if len(prices) < period + 1:
return [None] * len(prices)
deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
gains = [max(d, 0) for d in deltas]
losses = [abs(min(d, 0)) for d in deltas]


avg_gain = sum(gains[:period]) / period
avg_loss = sum(losses[:period]) / period
rs = avg_gain / avg_loss if avg_loss != 0 else float('inf')
rsi = [None] * (period)
rsi.append(100 - (100 / (1 + rs)))


for i in range(period, len(gains)):
avg_gain = (avg_gain * (period - 1) + gains[i]) / period
avg_loss = (avg_loss * (period - 1) + losses[i]) / period
rs = avg_gain / avg_loss if avg_loss != 0 else float('inf')
rsi.append(100 - (100 / (1 + rs)))


return [None] + rsi


# MACD
def calc_macd(prices, fast=12, slow=26, signal=9):
ema_fast = calc_ema(prices, fast)
ema_slow = calc_ema(prices, slow)
macd = []
for a, b in zip(ema_fast, ema_slow):
macd.append(a - b)
signal_line = calc_ema(macd, signal) if macd else []
return macd, signal_line


# Simple linear forecast
def simple_forecast(prices, lookback=20, horizon=6):
if len(prices) < lookback:
return []
x = list(range(lookback))
y = prices[-lookback:]
n = lookback
sum_x = sum(x)
sum_y = sum(y)
sum_xx = sum([xi * xi for xi in x])
sum_xy = sum([xi * yi for xi, yi in zip(x, y)])
denom = n * sum_xx - sum_x * sum_x
if denom == 0:
return []
a = (n * sum_xy - sum_x * sum_y) / denom
b = (sum_y - a * sum_x) / n
preds = []
for t in range(lookback, lookback + horizon):
preds.append(a * t + b)
return preds
