from fastapi import FastAPI
from pydantic import BaseModel

from tools.query_router import route_query
from llm.prompt_chain import generate_strategy_response

app = FastAPI(title="AI SaaS Ad Strategy Copilot")


class QueryRequest(BaseModel):
    query: str
    model_name: str = "mistral"
    prompt_strategy: str = "meta_reflect"
    use_cache: bool = True


@app.get("/")
def root():
    return {"message": "AI SaaS Ad Strategy Copilot API is running"}


@app.post("/ask")
def ask_bot(request: QueryRequest):
    tool_result = route_query(request.query)

    response = generate_strategy_response(
        user_query=request.query,
        tool_context=tool_result,
        model_name=request.model_name,
        prompt_strategy=request.prompt_strategy,
        use_cache=request.use_cache
    )

    return {
        "query": request.query,
        "model_name": request.model_name,
        "prompt_strategy": request.prompt_strategy,
        "tool_result": tool_result,
        "response": response
    }