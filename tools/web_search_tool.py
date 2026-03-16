import os


def mock_web_search(query: str):
    mock_results = [
        {
            "title": "Top SaaS Advertising Trends",
            "snippet": "AI-driven personalization and ROI-focused messaging remain dominant trends in SaaS marketing."
        },
        {
            "title": "Competitor Ad Strategy Insights",
            "snippet": "Competitors are emphasizing productivity, automation, and cost reduction in recent campaigns."
        }
    ]
    return {
        "query": query,
        "results": mock_results
    }


def web_search(query: str):
    mode = os.getenv("WEB_SEARCH_MODE", "mock")
    if mode == "mock":
        return mock_web_search(query)

    # Later you can replace this with SerpAPI or Tavily integration
    return mock_web_search(query)