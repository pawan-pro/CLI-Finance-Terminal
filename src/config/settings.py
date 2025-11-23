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
def load_alpha_vantage_keys():
    """Loads all Alpha Vantage API keys from environment variables."""
    keys = []
    base_key_name = "ALPHA_VANTAGE_API_KEY"

    # Load the primary key
    primary_key = os.getenv(base_key_name)
    if primary_key:
        keys.append(primary_key)

    # Load numbered keys (e.g., ALPHA_VANTAGE_API_KEY_1, _2, etc.)
    i = 1
    while True:
        numbered_key = os.getenv(f"{base_key_name}_{i}")
        if numbered_key:
            keys.append(numbered_key)
            i += 1
        else:
            break

    return keys

api_keys = {
    "alpha_vantage": load_alpha_vantage_keys(),
    "polygon": os.getenv("POLYGON_API_KEY"),
    "newsapi": os.getenv("NEWS_API_KEY"),
}

settings["api_keys"] = api_keys

if __name__ == "__main__":
    from rich import print
    print(settings)
