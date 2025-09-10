import requests
from src.config.settings import settings
from src.data import cache_manager

class NewsAPI:
    def __init__(self):
        self.api_key = settings["api_keys"]["newsapi"]
        if not self.api_key:
            raise ValueError("NewsAPI key not found. Please set it in your .env file.")
        self.base_url = "https://newsapi.org/v2/top-headlines"

    def get_top_headlines(self, country="us", category="general", page_size=10):
        """Fetches top general headlines from a given country."""
        params = {
            "country": country,
            "category": category,
            "pageSize": page_size,
            "apiKey": self.api_key,
        }
        cache_key = cache_manager.get_cache_key("news", params)

        cached_data = cache_manager.get_from_cache(cache_key)
        if cached_data:
            return cached_data

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "ok" and "articles" in data:
                articles = data["articles"]
                cache_manager.set_to_cache(cache_key, articles)
                return articles
            else:
                print(f"Error from NewsAPI: {data.get('message')}")
                cache_manager.set_to_cache(cache_key, None)
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news from NewsAPI: {e}")
            cache_manager.set_to_cache(cache_key, None)
            return None
        except ValueError:
            print(f"Error decoding JSON from NewsAPI.")
            cache_manager.set_to_cache(cache_key, None)
            return None
