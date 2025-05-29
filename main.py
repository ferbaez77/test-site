from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Dict
import random
from datetime import datetime, timezone

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/signals")
async def read_signals_page(request: Request):
    return templates.TemplateResponse("signals.html", {"request": request})

@app.get("/api/signals")
async def get_trading_signals_api() -> List[Dict[str, any]]:
    trading_pairs = ["BTC/USD", "ETH/EUR", "ADA/USD", "SOL/USD", "DOT/USD"]
    signals = []
    num_signals = random.randint(3, 5)

    for _ in range(num_signals):
        signal = {
            "pair": random.choice(trading_pairs),
            "action": random.choice(["BUY", "SELL"]),
            "confidence": round(random.uniform(0.5, 0.99), 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        signals.append(signal)
    
    return signals
