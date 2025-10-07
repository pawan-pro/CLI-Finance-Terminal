import requests
from src.config.settings import settings
from src.data.cache_manager import cache_manager

class NewsAPI:
    def __init__(self):
        # Use Finnhub API key for news instead of separate NewsAPI key
        self.api_key = settings["api_keys"].get("finnhub")
        if not self.api_key:
            raise ValueError("FINNHUB_API_KEY not found. Please set it in your .env file.")
        self.base_url = "https://api.finnhub.io/api/v1/news"

    def get_financial_news(self, category="general", min_id=None):
        """
        Fetches financial news from Finnhub API.
        
        Args:
            category: News category ('general', 'forex', 'crypto', 'merger')
            min_id: Minimum ID to fetch news from
            
        Returns:
            List of news articles
        """
        params = {
            "category": category,
            "token": self.api_key
        }
        if min_id:
            params["minId"] = min_id
            
        cache_key = f"finnhub_financial_news_{category}_{min_id or 0}"

        cached_data = cache_manager.get(cache_key)
        if cached_data:
            return cached_data

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            articles = response.json()
            
            # Finnhub news API returns a list of news objects directly
            if isinstance(articles, list):
                cache_manager.set(cache_key, articles)
                return articles
            else:
                print(f"Error from Finnhub News API: {articles}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news from Finnhub News API: {e}")
            return []
        except ValueError as e:
            print(f"Error decoding JSON from Finnhub News API: {e}")
            return []