from fastapi import FastAPI
from pydantic import BaseModel

from tools.query_router import route_query
from llm.prompt_chain import generate_strategy_response

app = FastAPI(title="AI SaaS Ad Strategy Copilot")


class QueryRequest(BaseModel):
    query: str
    model_name: str = "mistral"


@app.get("/")
def root():
    return {"message": "AI SaaS Ad Strategy Copilot API is running"}


@app.post("/ask")
def ask_bot(request: QueryRequest):
    tool_result = route_query(request.query)
    response = generate_strategy_response(
        user_query=request.query,
        tool_context=tool_result,
        model_name=request.model_name
    )
    return {
        "query": request.query,
        "tool_result": tool_result,
        "response": response
    }