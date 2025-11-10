# main.py

from agent import news_agent
import json

if __name__ == "__main__":
    # Path to your daily report file
    report_path = "/Users/pawan/CLI-Finance-Terminal/approach 2.0/daily_report-i.html"
    # Your free NewsAPI key (replace with your own API key)
    #news_api_key = "e0a640b1e9e445b48b6291d595479f27"
    news_api_key = "4ac357ac9bf64b83ba8bfb5fc86f11b6"
    #news_api_key = "b85495a5-602a-4bb5-ade4-2c86d87d51ba"

    results = news_agent(report_path, news_api_key)

    # Output JSON for inspection (could format into HTML/Markdown later)
    with open("/Users/pawan/CLI-Finance-Terminal/approach 2.0/financial-news/asset_news.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"Fetched news for {len(results)} asset headlines. Output saved to asset_news.json.")

