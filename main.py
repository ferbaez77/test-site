from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Dict
import random
from datetime import datetime, timezone
from services.crypto_data import get_top_crypto_data, get_coin_details, get_ohlcv_data

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
async def get_trading_signals_api() -> List[Dict[str, any]]: # Renamed to avoid conflict if we add a page at /signals
    trading_pairs = ["BTC/USD", "ETH/EUR", "ADA/USD", "SOL/USD", "DOT/USD"] # Example pairs
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

@app.get("/api/homepage_cryptos")
async def get_homepage_cryptos_data():
    try:
        crypto_list = get_top_crypto_data(limit=25) # Or your desired limit
        if not crypto_list:
            # This handles the case where get_top_crypto_data returns an empty list due to an API error
            raise HTTPException(status_code=503, detail="Service temporarily unavailable: Could not fetch cryptocurrency data from external provider.")
        return crypto_list
    except Exception as e:
        # Catch any other unexpected errors during the process
        # Log the error e for debugging
        print(f"An unexpected error occurred in /api/homepage_cryptos: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

@app.get("/api/predict/{crypto_id}")
async def get_mock_prediction(crypto_id: str, crypto_name: str = None): # crypto_name can be passed as a query param
    predicted_trend = random.choice(["UP", "DOWN", "SIDEWAYS"]) # Added SIDEWAYS for more variety
    mock_confidence = random.randint(60, 95) # Adjusted range slightly

    # Use the provided crypto_name if available, otherwise capitalize the ID
    display_name = crypto_name if crypto_name else crypto_id.capitalize()

    message = f"AI Mock Prediction for {display_name}: Expected trend is {predicted_trend} with {mock_confidence}% confidence (simulated)."

    return {
        "crypto_id": crypto_id,
        "crypto_name": display_name,
        "predicted_trend": predicted_trend,
        "mock_confidence_score": f"{mock_confidence}%",
        "message": message
    }

@app.get("/crypto/{crypto_id}")
async def crypto_detail_page(request: Request, crypto_id: str):
    coin_details = get_coin_details(crypto_id)
    return templates.TemplateResponse("crypto_detail.html", {"request": request, "coin": coin_details})

@app.get("/api/crypto_ohlcv/{crypto_id}")
async def get_crypto_ohlcv_api(crypto_id: str, days: int = Query(30, ge=1, le=365)): # Example: days as query param, default 30, min 1, max 365
    ohlcv_data = get_ohlcv_data(crypto_id, days=days)
    if not ohlcv_data:
        raise HTTPException(status_code=404, detail=f"OHLCV data not found for {crypto_id} for the last {days} days, or an error occurred.")
    return ohlcv_data
