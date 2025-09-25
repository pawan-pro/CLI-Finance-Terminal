import requests
from src.config.settings import settings
from src.data.cache_manager import cache_manager

class NewsAPI:
    def __init__(self):
        self.api_key = settings["api_keys"]["newsapi"]
        if not self.api_key:
            raise ValueError("NewsAPI key not found. Please set it in your .env file.")
        self.base_url = "https://newsapi.org/v2/everything"

    def get_financial_news(self, query="finance", page_size=7):
        """Fetches top financial news headlines."""
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "apiKey": self.api_key,
        }
        # Simplified cache key for financial news
        cache_key = "financial_news"

        cached_data = cache_manager.get(cache_key)
        if cached_data:
            return cached_data

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
            if data.get("status") == "ok" and "articles" in data:
                articles = data["articles"]
                cache_manager.set(cache_key, articles)
                return articles
            else:
                print(f"Error from NewsAPI: {data.get('message')}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news from NewsAPI: {e}")
            return None
        except ValueError:
            print("Error decoding JSON from NewsAPI.")
            return None
