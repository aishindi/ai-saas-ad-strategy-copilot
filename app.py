import os
import time
from cachetools import TTLCache
from fastapi import FastAPI
from pydantic import BaseModel

from tools.query_router import route_query
from llm.prompt_chain import generate_strategy_response
from security.guardrails import is_prompt_injection, get_guardrail_response

app = FastAPI(title="AI SaaS Ad Strategy Copilot")

# API-level cache: caches full backend response
api_cache = TTLCache(maxsize=200, ttl=600)


class QueryRequest(BaseModel):
    query: str
    model_name: str = "mistral"
    prompt_strategy: str = "meta_reflect"
    use_cache: bool = True
    web_search_mode: str = "mock"
    tavily_api_key: str | None = None


def normalize_text(text: str) -> str:
    return " ".join(text.lower().strip().split())


def build_api_cache_key(request: QueryRequest) -> str:
    return "|".join([
        normalize_text(request.query),
        request.model_name,
        request.prompt_strategy,
        request.web_search_mode
    ])


def is_valid_query(query: str):
    query = query.strip().lower()

    if len(query) < 10:
        return False

    if " " not in query and "?" not in query:
        return False

    domain_keywords = [
        "budget", "campaign", "ad", "ads", "advertising", "platform",
        "linkedin", "google", "meta", "twitter",
        "roi", "cac", "conversion", "conversions", "clicks", "impressions",
        "audience", "segment", "targeting", "customer acquisition",
        "competitor", "trend", "keywords", "market",
        "saas", "b2b", "funnel", "messaging", "performance",
        "strategy", "optimize", "underperforming"
    ]

    return any(keyword in query for keyword in domain_keywords)


def get_validation_response():
    return {
        "cached": False,
        "response": "Please enter a valid SaaS advertising strategy question. For example, ask about budget allocation, audience targeting, ROI, CAC, platform comparison, or competitor trends.",
        "response_time_sec": 0.0,
        "prompt_strategy": "validation",
        "model_name": "none"
    }


@app.get("/")
def root():
    return {"message": "AI SaaS Ad Strategy Copilot API is running"}


@app.post("/ask")
def ask_bot(request: QueryRequest):
    os.environ["WEB_SEARCH_MODE"] = request.web_search_mode

    if request.tavily_api_key:
        os.environ["TAVILY_API_KEY"] = request.tavily_api_key

    cache_key = build_api_cache_key(request)

    # Serve cached full response before routing/tools/LLM
    if request.use_cache and cache_key in api_cache:
        cached_payload = api_cache[cache_key]
        cached_payload["response"]["cached"] = True
        cached_payload["response"]["response_time_sec"] = 0.0
        return cached_payload

    if not is_valid_query(request.query):
        payload = {
            "query": request.query,
            "model_name": request.model_name,
            "prompt_strategy": request.prompt_strategy,
            "tool_result": {
                "tool_used": "validation",
                "data": "Invalid or unclear query blocked before tool or LLM execution."
            },
            "response": get_validation_response()
        }
        return payload

    if is_prompt_injection(request.query):
        payload = {
            "query": request.query,
            "model_name": request.model_name,
            "prompt_strategy": request.prompt_strategy,
            "tool_result": {
                "tool_used": "guardrail",
                "data": "Prompt injection attempt blocked before tool or LLM execution."
            },
            "response": get_guardrail_response()
        }
        return payload

    start = time.time()

    tool_result = route_query(request.query)

    response = generate_strategy_response(
        user_query=request.query,
        tool_context=tool_result,
        model_name=request.model_name,
        prompt_strategy=request.prompt_strategy,
        use_cache=request.use_cache
    )

    response["cached"] = False
    response["response_time_sec"] = round(time.time() - start, 3)

    payload = {
        "query": request.query,
        "model_name": request.model_name,
        "prompt_strategy": request.prompt_strategy,
        "tool_result": tool_result,
        "response": response
    }

    if request.use_cache:
        api_cache[cache_key] = payload

    return payload