import pytest
import json

@pytest.fixture
def mock_api_request(mocker):
    """Mocks the _make_request method of AlphaVantageDataFetcher."""

    def mock_request_handler(params, ttl):
        function = params.get('function')
        symbol = params.get('symbol')
        from_currency = params.get('from_currency')

        if function == 'GLOBAL_QUOTE':
            if symbol == 'SPY':
                return {"Global Quote": {"05. price": "500.00", "10. change percent": "0.5%"}}
            elif symbol == "IBM":
                return {"Global Quote": {"05. price": "150.00", "10. change percent": "-1.2%"}}
            else:
                return {"Global Quote": {}}

        elif function == 'CURRENCY_EXCHANGE_RATE':
            if from_currency == 'EUR':
                return {"Realtime Currency Exchange Rate": {"5. Exchange Rate": "1.08"}}
            else:
                return {}

        elif function == 'DIGITAL_CURRENCY_DAILY':
            if params.get('symbol') == 'BTC':
                return {
                    "Time Series (Digital Currency Daily)": {
                        "2025-10-08": {"4a. close (USD)": "70000.00"},
                        "2025-10-07": {"4a. close (USD)": "69000.00"}
                    }
                }
            else:
                return {}

        elif function == 'TIME_SERIES_DAILY_ADJUSTED':
            return {
                "Time Series (Daily)": {
                    "2025-10-08": {"5. adjusted close": "501.00"},
                    "2025-10-07": {"5. adjusted close": "500.00"}
                }
            }

        elif function == 'FX_DAILY':
             return {
                "Time Series FX (Daily)": {
                    "2025-10-08": {"4. close": "1.08"},
                    "2025-10-07": {"4. close": "1.07"}
                }
            }

        elif function == 'TIME_SERIES_INTRADAY':
             return {
                f"Time Series ({params.get('interval')})": {
                    "2025-10-08 16:00:00": {
                        "1. open": "500.0", "2. high": "501.0", "3. low": "499.0", "4. close": "500.5", "5. volume": "100000"
                    }
                }
            }

        return None # Default empty response

    return mocker.patch(
        'src.data.providers.alphavantage_data.AlphaVantageDataFetcher._make_request',
        side_effect=mock_request_handler
    )