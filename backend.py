from fastapi import FastAPI
import ccxt
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import requests
import asyncio

load_dotenv()

app = FastAPI()

# MEXC API Keys
API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

# Initialize MEXC Exchange
exchange = ccxt.mexc({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'options': {'adjustForTimeDifference': True}
})

@app.get("/balance")
def get_balance():
    try:
        balance = exchange.fetch_balance()
        return {"status": "success", "balance": balance}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/trade-history")
def get_trade_history():
    try:
        trades = exchange.fetch_my_trades()
        return {"status": "success", "trades": trades}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/place-order")
def place_order(symbol: str, side: str, amount: float, price: float = None, order_type: str = "limit"):
    try:
        order = exchange.create_order(symbol, order_type, side, amount, price)
        return {"status": "success", "order": order}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/market-news")
def get_market_news():
    try:
        response = requests.get("https://newsapi.org/v2/top-headlines?category=business&apiKey=" + os.getenv("NEWS_API_KEY"))
        return {"status": "success", "news": response.json().get("articles", [])}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
