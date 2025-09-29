import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class AlphaVantageData:
    def __init__(self):
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "YOUR_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"

    def get_bond_etf_data(self, symbols: list):
        """
        Fetches the latest quote for a list of bond and ETF symbols.
        """
        bond_etf_data = []
        for symbol in symbols:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            try:
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json().get('Global Quote', {})
                if data:
                    bond_etf_data.append({
                        'name': data.get('01. symbol'),
                        'description': f"{symbol} ETF/Bond",
                        'Price': float(data.get('05. price')),
                        'change': float(data.get('09. change')),
                        'pct_change': float(data.get('10. change percent').replace('%', ''))
                    })
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data for {symbol} from Alpha Vantage: {e}")
        
        return pd.DataFrame(bond_etf_data)
