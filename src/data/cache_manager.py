import json
from pathlib import Path
import time
from src.config.settings import settings

CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)
CACHE_DURATION = settings.get("cache_duration_seconds", 3600)
CACHE_DURATION_FAILED = 300 # 5 minutes for failed requests

def get_cache_key(prefix: str, params: dict) -> str:
    """Creates a unique cache key from a prefix and params."""
    param_str = "_".join(f"{k}_{v}" for k, v in sorted(params.items()))
    return f"{prefix}_{param_str}.json"

def get_from_cache(key: str):
    """Gets data from the cache if it's not stale."""
    cache_file = CACHE_DIR / key
    if cache_file.exists():
        now = time.time()
        file_mod_time = cache_file.stat().st_mtime

        with open(cache_file, "r") as f:
            data = json.load(f)

        duration = CACHE_DURATION if data is not None else CACHE_DURATION_FAILED

        if (now - file_mod_time) < duration:
            return data

    return None

def set_to_cache(key: str, data: dict):
    """Saves data to the cache."""
    cache_file = CACHE_DIR / key
    with open(cache_file, "w") as f:
        json.dump(data, f, indent=4)
