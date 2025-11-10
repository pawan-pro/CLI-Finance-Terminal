import os
import json
from google.adk.agents import Agent
import google.generativeai as genai
from dotenv import load_dotenv

# Load your API key from .env file
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if api_key is None:
    raise ValueError("GOOGLE_API_KEY not found in .env")

# Configure generativeai client with API key
genai.configure(api_key=api_key)

def summarize_news_with_llm(json_path: str) -> dict:
    """
    Uses Gemini LLM to summarize financial news from JSON and outputs Markdown.
    """
    try:
        with open(json_path, 'r') as f:
            news_list = json.load(f)

        # Build prompt for LLM: Concatenate headlines and summaries
        prompt_lines = []
        for item in news_list:
            asset = item.get("asset", "")
            title = item.get("title", "")
            summary = item.get("summary", "")
            prompt_lines.append(f"{asset}: {title} — {summary}")
        news_block = "\n".join(prompt_lines)

        prompt = (
            "You are an expert financial news analyst. Summarize the following news headlines and summaries "
            "into a concise, market-oriented digest suitable for a daily investment report. "
            "Highlight major developments and overall sentiment.\n\n"
            + news_block
        )

        # Call Gemini
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        # Get the summary text from the LLM response
        summary_text = response.text if hasattr(response, "text") else str(response)

        # Save summary to markdown
        md_filename = "/Users/pawan/CLI-Finance-Terminal/approach 2.0/financial-news/summarizer-agent/news_digest_llm.md"
        with open(md_filename, "w") as f:
            f.write("# Financial News Digest\n\n")
            f.write(summary_text.strip() + "\n")

        return {
            "status": "success",
            "report": f"LLM news summary written to {md_filename}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to summarize news with LLM: {str(e)}"
        }

# Wrap in ADK agent
root_agent = Agent(
    name="news_summarizer_llm_agent",
    model="gemini-2.0-flash",
    description="Agent uses Gemini LLM to summarize financial news and output Markdown.",
    instruction="You are a helpful agent who summarizes financial news in JSON format using Gemini LLM and outputs a Markdown digest.",
    tools=[summarize_news_with_llm],
)

# Optional: Command-line entry for test run
if __name__ == "__main__":
    test_json_path = "/Users/pawan/CLI-Finance-Terminal/approach 2.0/financial-news/asset_news.json"
    result = summarize_news_with_llm(test_json_path)
    print(result)
