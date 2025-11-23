import threading
from itertools import cycle
from src.config.settings import settings

class APIKeyManager:
    """
    Manages and rotates a list of Alpha Vantage API keys.
    This class is implemented as a thread-safe singleton.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Another check for thread safety
                if cls._instance is None:
                    cls._instance = super(APIKeyManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Ensure __init__ is called only once
        if hasattr(self, '_initialized'):
            return

        with self._lock:
            if hasattr(self, '_initialized'):
                return

            self.keys = settings.get("api_keys", {}).get("alpha_vantage", [])
            if not self.keys:
                raise ValueError("No Alpha Vantage API keys found. Please set ALPHA_VANTAGE_API_KEY and/or ALPHA_VANTAGE_API_KEY_n in your .env file.")

            self.key_cycle = cycle(self.keys)
            self._initialized = True

    def get_key(self) -> str:
        """
        Returns the next available API key in a round-robin fashion.
        """
        with self._lock:
            key = next(self.key_cycle)
            return key

# Singleton instance for easy access across the application
api_key_manager = APIKeyManager()