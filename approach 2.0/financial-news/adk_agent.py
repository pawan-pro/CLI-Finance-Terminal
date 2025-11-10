from adk import BaseAgent

class NewsAgent(BaseAgent):
    def __init__(self, news_api_key):
        super().__init__()
        self.news_api_key = news_api_key
        self.name = "NewsAgent"

    def run(self, report_path):
        from agent import extract_asset_names, fetch_news
        assets = extract_asset_names(report_path)
        summary = []
        for asset in assets:
            headlines = fetch_news(self.news_api_key, asset)
            for h in headlines:
                summary.append({
                    "asset": asset,
                    "title": h["title"],
                    "url": h["url"],
                    "summary": h["summary"]
                })
        return summary

# Example usage
if __name__ == "__main__":
    agent = NewsAgent(news_api_key="e0a640b1e9e445b48b6291d595479f27")
    news_result = agent.execute_with_error_handling("/Users/pawan/CLI-Finance-Terminal/approach 2.0/financial-news/asset_news.json")
    print(news_result)
