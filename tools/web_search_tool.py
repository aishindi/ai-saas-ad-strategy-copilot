import os
import requests
from dotenv import load_dotenv

load_dotenv()


def mock_web_search(query: str):
    mock_results = [
        {
            "title": "Top SaaS Advertising Trends",
            "snippet": "AI-driven personalization, ROI-focused messaging, and automation remain major SaaS marketing themes."
        },
        {
            "title": "Competitor Ad Strategy Insights",
            "snippet": "Competitors are emphasizing productivity, cost reduction, and workflow automation in recent campaigns."
        },
        {
            "title": "Seasonal SaaS Demand Signals",
            "snippet": "Q3 and Q4 often show increased enterprise buying activity, especially for budget planning and workflow software."
        }
    ]
    return {
        "query": query,
        "source": "mock",
        "results": mock_results
    }


def tavily_web_search(query: str):
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return mock_web_search(query)

    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": 5
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        formatted_results = []
        for item in data.get("results", []):
            formatted_results.append({
                "title": item.get("title", ""),
                "snippet": item.get("content", ""),
                "url": item.get("url", "")
            })

        return {
            "query": query,
            "source": "tavily",
            "results": formatted_results
        }

    except Exception as e:
        return {
            "query": query,
            "source": "fallback_mock",
            "error": str(e),
            "results": mock_web_search(query)["results"]
        }


def web_search(query: str):
    mode = os.getenv("WEB_SEARCH_MODE", "mock").lower()

    if mode == "tavily":
        return tavily_web_search(query)

    return mock_web_search(query)