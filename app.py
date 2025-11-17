from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import plotly.graph_objs as go
from crypto import get_price_history, get_trend
import plotly.io as pio

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, symbol: str = "bitcoin"):
    prices = await get_price_history(symbol)
    trend = get_trend(prices)

    # Создаём график Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[p[0] for p in prices],
        y=[p[1] for p in prices],
        mode='lines',
        name=symbol
    ))
    graph_html = pio.to_html(fig, full_html=False)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "symbol": symbol,
        "trend": trend,
        "graph": graph_html
    })
