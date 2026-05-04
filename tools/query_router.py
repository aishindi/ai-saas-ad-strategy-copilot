from tools.db_tool import (
    get_top_roi_segments,
    compare_platforms,
    get_underperforming_campaigns,
    get_best_regions_by_cac,
)
from tools.web_search_tool import web_search


def route_query(user_query: str):
    lower_q = user_query.lower()

    if "highest roi" in lower_q or "audience segment" in lower_q:
        return {
            "tool_used": "database",
            "data": get_top_roi_segments()
        }

    if "compare linkedin" in lower_q and "google" in lower_q:
        return {
            "tool_used": "database",
            "data": compare_platforms("LinkedIn", "Google")
        }

    if "underperforming campaign" in lower_q:
        return {
            "tool_used": "database",
            "data": get_underperforming_campaigns()
        }

    if "customer acquisition cost" in lower_q or "geographic regions" in lower_q or "best regions" in lower_q:
        return {
            "tool_used": "database",
            "data": get_best_regions_by_cac()
        }

    if (
        "competitor" in lower_q
        or "trending" in lower_q
        or "seasonal" in lower_q
        or "keywords" in lower_q
        or "market trends" in lower_q
    ):
        return {
            "tool_used": "web_search",
            "data": web_search(user_query)
        }

    return {
        "tool_used": "hybrid",
        "data": {
            "db_data": get_top_roi_segments(),
            "web_data": web_search(user_query)
        }
    }