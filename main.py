from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head><title>Crypto Trend</title></head>
        <body>
            <h1>Crypto Trend</h1>
            <p>Направление рынка: 🚀</p>
            <p>Тренд выбранной монеты: 🔥</p>
            <p>График цены: (будет здесь)</p>
            <p>Прогноз: (опционально)</p>
        </body>
    </html>
    """
