import time
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(
    page_title="AI SaaS Ad Strategy Copilot",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
header[data-testid="stHeader"] {
    display: none;
}

#MainMenu, footer {
    visibility: hidden;
}

.stApp {
    background: linear-gradient(180deg, #06101f 0%, #07182c 45%, #08213d 100%);
    color: #eaf4ff;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 7rem !important;
    max-width: 1050px;
}

section[data-testid="stSidebar"] {
    background: #040d19;
    border-right: 1px solid rgba(255,255,255,0.08);
}

.sidebar-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.4;
    margin-bottom: 0.4rem;
}

.sidebar-subtitle {
    color: #8ab6dd;
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
}

.main-title {
    text-align: center;
    font-size: 2.7rem;
    font-weight: 850;
    color: #ffffff;
    margin-top: 0rem;
    margin-bottom: 0.3rem;
}

.main-subtitle {
    text-align: center;
    color: #9fc7ed;
    font-size: 1rem;
    margin-bottom: 1.8rem;
}

.card-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
    margin-top: 1rem;
    margin-bottom: 2rem;
}

.prompt-card {
    background: rgba(14, 35, 59, 0.95);
    border: 1px solid rgba(58, 178, 255, 0.22);
    border-radius: 14px;
    padding: 16px;
    color: #e8f4ff;
    min-height: 72px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.18);
    font-size: 0.95rem;
}

div[data-testid="stChatMessage"] {
    background: rgba(8, 25, 45, 0.78);
    border-radius: 16px;
    padding: 0.35rem 0.7rem;
    border: 1px solid rgba(255,255,255,0.07);
}

div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] li {
    color: #eaf4ff !important;
    font-size: 0.95rem;
    line-height: 1.6;
}

div[data-testid="stChatMessage"] h1,
div[data-testid="stChatMessage"] h2,
div[data-testid="stChatMessage"] h3,
div[data-testid="stChatMessage"] strong {
    color: #ffffff !important;
}

div[data-testid="stChatInput"] {
    position: fixed;
    bottom: 0;
    left: 260px;
    right: 0;
    padding: 14px 28px 18px 28px;
    background: linear-gradient(
        180deg,
        rgba(6,16,31,0) 0%,
        rgba(6,16,31,0.96) 35%,
        rgba(6,16,31,1) 100%
    );
    border-top: 1px solid rgba(255,255,255,0.08);
    z-index: 100;
}

div[data-testid="stChatInput"] > div {
    width: 100% !important;
    min-height: 54px !important;
    background: rgba(8, 25, 45, 0.98) !important;
    border: 1px solid rgba(120,180,255,0.35) !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 30px rgba(0,0,0,0.25);
}

div[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #ffffff !important;
    caret-color: #ffffff !important;
    font-size: 0.96rem !important;
    padding: 12px 14px !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: #a9c5de !important;
}
            
.sticky-header {
    position: sticky;
    top: 0;
    z-index: 90;
    padding: 20px 0 18px 0;
    background: linear-gradient(
        180deg,
        rgba(6,16,31,1) 0%,
        rgba(6,16,31,0.95) 70%,
        rgba(6,16,31,0) 100%
    );
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255,255,255,0.06);
}

.stButton button {
    background: linear-gradient(90deg, #15b9ff, #7b61ff);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.58rem 1.3rem;
    font-weight: 750;
}
            
label, .stSelectbox label, .stTextInput label, .stCheckbox label {
    color: #b9d7f2 !important;
    font-weight: 600 !important;
}

.status-pill {
    display: inline-block;
    background: rgba(21, 185, 255, 0.12);
    color: #8fdcff;
    border: 1px solid rgba(21, 185, 255, 0.28);
    border-radius: 999px;
    padding: 5px 10px;
    font-size: 0.78rem;
    margin-right: 6px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)


def stream_response(text: str):
    words = text.split(" ")
    output = ""
    placeholder = st.empty()

    for word in words:
        output += word + " "
        placeholder.markdown(output)
        time.sleep(0.01)

    return output


def is_follow_up_query(query: str) -> bool:
    q = query.lower().strip()

    followup_terms = [
        "that", "this", "those", "them", "it",
        "previous", "above", "same", "again",
        "what about", "how about", "compare with",
        "can you explain", "why", "also"
    ]

    return any(term in q for term in followup_terms)


def build_contextual_query(current_query: str) -> str:
    if not st.session_state.messages:
        return current_query

    if not is_follow_up_query(current_query):
        return current_query

    recent_messages = st.session_state.messages[-4:]
    conversation_context = "\n\nPrevious conversation context:\n"

    for msg in recent_messages:
        conversation_context += f"{msg['role'].upper()}: {msg['content']}\n"

    return f"""
{conversation_context}

Current follow-up question:
{current_query}
"""


if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_run_details" not in st.session_state:
    st.session_state.last_run_details = None


with st.sidebar:
    # st.markdown(
    #     '<div class="sidebar-title">AI SaaS Ad Strategy<br>Copilot</div>',
    #     unsafe_allow_html=True
    # )
    # st.markdown(
    #     '<div class="sidebar-subtitle">Strategic marketing intelligence for SaaS growth</div>',
    #     unsafe_allow_html=True
    # )

    if st.button("＋ New Analysis", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_run_details = None
        st.rerun()

    model_name = st.selectbox("Choose model", ["mistral", "llama3"])
    prompt_strategy = st.selectbox("Choose prompt strategy", ["baseline", "meta", "meta_reflect"])
    use_cache = st.checkbox("Use cache", value=True)

    st.markdown("---")
    web_search_mode = st.selectbox("Web search mode", ["mock", "tavily"])
    tavily_api_key = st.text_input("Tavily API Key (optional)", type="password")

    if st.session_state.last_run_details:
        st.markdown("---")
        st.markdown("### Last Run")
        st.markdown(
            f"""
            <span class="status-pill">Model: {st.session_state.last_run_details["model"]}</span><br>
            <span class="status-pill">Strategy: {st.session_state.last_run_details["strategy"]}</span><br>
            <span class="status-pill">Cached: {st.session_state.last_run_details["cached"]}</span><br>
            <span class="status-pill">Time: {st.session_state.last_run_details["time"]}s</span>
            """,
            unsafe_allow_html=True
        )


# st.markdown('<div class="main-title">AI SaaS Ad Strategy Copilot</div>', unsafe_allow_html=True)
# st.markdown(
#     '<div class="main-subtitle">Ask strategic questions about budget allocation, audience targeting, campaign performance, and competitor trends.</div>',
#     unsafe_allow_html=True
# )
st.markdown("""
    <div class="sticky-header">
        <div class="main-title">AI SaaS Ad Strategy Copilot</div>
        <div class="main-subtitle">
            Ask strategic questions about budget allocation, audience targeting, campaign performance, and competitor trends.
        </div>
    </div>
    """, unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="card-row">
        <div class="prompt-card">Recommend budget allocation for a $50K B2B SaaS launch across LinkedIn, Google, and Meta.</div>
        <div class="prompt-card">Which audience segment historically produced the highest ROI?</div>
        <div class="prompt-card">Compare LinkedIn Ads and Google Ads performance for enterprise SaaS campaigns.</div>
        <div class="prompt-card">Analyze competitor messaging and keyword trends for AI productivity SaaS.</div>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

query = st.chat_input("Ask your SaaS ad strategy question...")

if query:
    contextual_query = build_contextual_query(query)

    st.session_state.messages.append({
        "role": "user",
        "content": query
    })

    with st.chat_message("user"):
        st.markdown(query)

    payload = {
        "query": contextual_query,
        "model_name": model_name,
        "prompt_strategy": prompt_strategy,
        "use_cache": use_cache,
        "web_search_mode": web_search_mode,
        "tavily_api_key": tavily_api_key.strip() if tavily_api_key else None
    }

    with st.chat_message("assistant"):
        with st.spinner("Thinking through campaign data and strategy..."):
            try:
                response = requests.post(API_URL, json=payload, timeout=180)

                if response.status_code == 200:
                    data = response.json()
                    answer = data["response"]["response"]
                    final_text = stream_response(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": final_text
                    })

                    st.session_state.last_run_details = {
                        "model": data.get("model_name", model_name),
                        "strategy": data.get("prompt_strategy", prompt_strategy),
                        "cached": data["response"].get("cached", False),
                        "time": data["response"].get("response_time_sec", 0)
                    }

                else:
                    error_msg = "Failed to get response from backend."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

            except requests.exceptions.RequestException as e:
                error_msg = f"Backend connection error: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})