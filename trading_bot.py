import time
import logging
import requests
import os
from textblob import TextBlob
from mexc_api import MEXCClient
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

API_KEY = os.getenv("MEXC_API_KEY", "your_api_key_here")
API_SECRET = os.getenv("MEXC_API_SECRET", "your_api_secret_here")
BACKEND_URL = os.getenv("BACKEND_URL", "https://your-backend-url.com")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TradingBot:
    def __init__(self, api_key, api_secret, symbol, trade_amount, backend_url):
        self.client = MEXCClient(api_key, api_secret)
        self.symbol = symbol
        self.trade_amount = trade_amount
        self.last_price = self.client.get_price(symbol)
        self.backend_url = backend_url  # URL to fetch news

    def get_news_sentiment(self):
        """Fetch latest market news and analyze sentiment."""
        try:
            response = requests.get(f"{self.backend_url}/market-news")
            news_data = response.json()
            
            if news_data["status"] != "success":
                logging.warning("Failed to fetch news")
                return 0  # Neutral sentiment
            
            headlines = [article["title"] for article in news_data["news"]]
            sentiment_score = sum(TextBlob(title).sentiment.polarity for title in headlines) / len(headlines)
            return sentiment_score
        except Exception as e:
            logging.error(f"Error fetching news sentiment: {str(e)}")
            return 0

    def strategy(self):
        """Strategy: Buy on 2% dip if sentiment is positive, sell on 2% rise if negative."""
        try:
            price = self.client.get_price(self.symbol)
            sentiment = self.get_news_sentiment()
            logging.info(f"Current price: {price}, Sentiment Score: {sentiment}")
            
            if price < self.last_price * 0.98 and sentiment > 0:
                logging.info("Price dropped 2% and sentiment is positive, executing buy trade.")
                self.place_trade('buy')
            elif price > self.last_price * 1.02 and sentiment < 0:
                logging.info("Price increased 2% and sentiment is negative, executing sell trade.")
                self.place_trade('sell')
            
            self.last_price = price
        except Exception as e:
            logging.error(f"Error in strategy execution: {str(e)}")

    def place_trade(self, side):
        """Place a trade with risk management."""
        try:
            order = self.client.create_order(self.symbol, side, self.trade_amount)
            if order:
                logging.info(f"Trade executed: {side} {self.trade_amount} {self.symbol}")
        except Exception as e:
            logging.error(f"Trade failed: {str(e)}")

    def run(self):
        logging.info("Starting trading bot...")
        while True:
            self.strategy()
            time.sleep(10)  # Adjust timing as needed

if __name__ == "__main__":
    bot = TradingBot(API_KEY, API_SECRET, 'BTCUSDT', 0.01, BACKEND_URL)
    bot.run()
