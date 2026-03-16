# AI SaaS Ad Strategy Copilot

A tool-augmented LLM virtual assistant that helps SaaS companies plan and optimize ad strategies using:
- structured campaign data from SQLite
- web search for external market trends
- open-source LLMs for strategic recommendations

## Features
- Budget allocation recommendations
- Audience targeting suggestions
- Campaign performance analysis
- Competitor/trend analysis from the web
- Prompt chaining
- Meta prompting
- Self-reflection prompting
- Prompt caching
- Prompt injection testing
- Comparison between two open-source LLMs

## Project Structure
- `database/`: SQLite schema, connection, seeding
- `tools/`: DB and web search tools
- `llm/`: prompt templates, model loading, caching
- `evaluation/`: test queries, metrics, security tests
- `ui/`: Streamlit frontend
- `app.py`: FastAPI backend entrypoint

## Run Steps

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Seed database
```bash
python database/seed_data.py
```
### 3. Start FastAPI backend
```bash
uvicorn app:app --reload
```

### 4. Start Streamlit UI
```bash
streamlit run ui/streamlit_app.py
```


---

# 3. `.env.example`

```env
MODEL_SMALL=mistral
MODEL_LARGE=llama3
WEB_SEARCH_MODE=mock
SERPAPI_KEY=your_key_here
TAVILY_API_KEY=your_key_here
