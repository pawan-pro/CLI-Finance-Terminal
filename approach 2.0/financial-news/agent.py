from bs4 import BeautifulSoup
import requests

def extract_asset_names(report_path):
    with open(report_path, "r") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    assets = set()
    # Asset tables
    for table in soup.find_all("table", {"class": "data-table"}):
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if cells:
                asset = cells[0].get_text(strip=True)
                if asset and not asset.isnumeric():
                    assets.add(asset)
    return list(assets)

import requests

def fetch_news(api_key, query):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "apiKey": api_key,
        "sortBy": "publishedAt",
        "pageSize": 4
    }
    response = requests.get(url, params=params)
    news = []
    if response.status_code == 200:
        data = response.json()
        for article in data["articles"]:
            news.append({
                "title": article["title"],
                "url": article["url"],
                "summary": article.get("description") or ""
            })
    return news

def news_agent(report_path, news_api_key):
    assets = extract_asset_names(report_path)
    summary = []
    for asset in assets:
        headlines = fetch_news(news_api_key, asset)
        for h in headlines:
            summary.append({
                "asset": asset,
                "title": h["title"],
                "url": h["url"],
                "summary": h["summary"]
            })
    return summary
