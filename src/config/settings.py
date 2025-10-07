import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

def load_config():
    """Loads YAML configuration from default and user files."""
    # Path to the default configuration file
    default_config_path = BASE_DIR / "config" / "default.yaml"

    # Path to the user configuration file
    user_config_path = BASE_DIR / "config" / "user.yaml"

    # Load default config
    with open(default_config_path, "r") as f:
        config = yaml.safe_load(f)

    # Load user config if it exists and merge it
    if user_config_path.exists():
        with open(user_config_path, "r") as f:
            user_config = yaml.safe_load(f)
            if user_config:
                # Recursive update
                def update_dict(d, u):
                    for k, v in u.items():
                        if isinstance(v, dict):
                            d[k] = update_dict(d.get(k, {}), v)
                        else:
                            d[k] = v
                    return d
                config = update_dict(config, user_config)

    return config

# Load configuration
settings = load_config()

# API Keys from environment variables
api_keys = {
    "alpha_vantage": os.getenv("ALPHA_VANTAGE_API_KEY"),
    "polygon": os.getenv("POLYGON_API_KEY"),
    "newsapi": os.getenv("NEWS_API_KEY"),
    "finnhub": os.getenv("FINNHUB_API_KEY"),
}

settings["api_keys"] = api_keys

if __name__ == "__main__":
    from rich import print
    print(settings)
