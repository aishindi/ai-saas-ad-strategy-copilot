import streamlit as st
import requests

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

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

.stApp {
    background: linear-gradient(180deg, #06101f 0%, #07182c 45%, #08213d 100%);
    color: #eaf4ff;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px;
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
    font-size: 3rem;
    font-weight: 850;
    color: #ffffff;
    margin-top: 0rem;
    margin-bottom: 0.4rem;
}

.main-subtitle {
    text-align: center;
    color: #9fc7ed;
    font-size: 1.05rem;
    margin-bottom: 2rem;
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
    padding: 18px;
    color: #e8f4ff;
    min-height: 78px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.18);
}

.prompt-card:hover {
    border: 1px solid rgba(118, 95, 255, 0.5);
    background: rgba(18, 43, 74, 0.98);
}

.small-label {
    color: #76d4ff;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    margin-bottom: 0.4rem;
}

div[data-testid="stTextArea"] textarea {
    background-color: #f7f9fc !important;
    color: #111827 !important;
    border-radius: 14px !important;
    border: 1px solid rgba(80, 190, 255, 0.55) !important;
    caret-color: #111827 !important;
}

div[data-testid="stTextArea"] textarea::placeholder {
    color: #64748b !important;
}

div[data-testid="stSelectbox"] div {
    color: #111827 !important;
}

.stButton button {
    background: linear-gradient(90deg, #15b9ff, #7b61ff);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.58rem 1.3rem;
    font-weight: 750;
}

.stButton button:hover {
    background: linear-gradient(90deg, #37c5ff, #8c78ff);
    color: white;
}

.chat-box {
    background: rgba(8, 25, 45, 0.92);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 18px;
    margin-top: 1rem;
}

.user-msg {
    background: rgba(28, 64, 102, 0.95);
    border-left: 4px solid #2fbfff;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 12px;
    color: #ffffff;
}

.assistant-msg {
    background: rgba(9, 38, 67, 0.96);
    border-left: 4px solid #8b6cff;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 18px;
    color: #eaf4ff;
}

.meta-text {
    color: #8ab6dd;
    font-size: 0.82rem;
    margin-bottom: 0.4rem;
}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_tool_context" not in st.session_state:
    st.session_state.last_tool_context = None

with st.sidebar:
    st.markdown('<div class="sidebar-title">AI SaaS Ad Strategy<br>Copilot</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">Strategic marketing intelligence for SaaS growth</div>', unsafe_allow_html=True)

    if st.button("＋ New Analysis", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_tool_context = None
        st.rerun()

    model_name = st.selectbox("Choose model", ["mistral", "llama3"])
    prompt_strategy = st.selectbox("Choose prompt strategy", ["baseline", "meta", "meta_reflect"])
    use_cache = st.checkbox("Use cache", value=True)

st.markdown('<div class="main-title">AI SaaS Ad Strategy Copilot</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="main-subtitle">Ask strategic questions about budget allocation, audience targeting, campaign performance, and competitor trends.</div>',
    unsafe_allow_html=True
)

if not st.session_state.messages:
    st.markdown("""
    <div class="card-row">
        <div class="prompt-card">Recommend budget allocation for a $50K B2B SaaS launch across LinkedIn, Google, and Meta.</div>
        <div class="prompt-card">Which audience segment historically produced the highest ROI?</div>
        <div class="prompt-card">Compare LinkedIn Ads and Google Ads performance for enterprise SaaS campaigns.</div>
        <div class="prompt-card">Analyze competitor messaging and keyword trends for AI productivity SaaS.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="small-label">ENTER YOUR QUESTION</div>', unsafe_allow_html=True)

query = st.text_area(
    "",
    placeholder="Ask about budget allocation, top-performing segments, CAC, funnel optimization, competitor trends, or channel mix...",
    height=110
)

submit = st.button("Generate Strategy")

if submit and query.strip():
    conversation_context = ""

    if st.session_state.messages:
        recent_messages = st.session_state.messages[-4:]
        conversation_context = "\n\nPrevious conversation context:\n"
        for msg in recent_messages:
            conversation_context += f"{msg['role'].upper()}: {msg['content']}\n"

    final_query = query

    if conversation_context:
        final_query = f"""
{conversation_context}

Current follow-up question:
{query}
"""

    with st.spinner("Generating strategic recommendation..."):
        response = requests.post(
            API_URL,
            json={
                "query": final_query,
                "model_name": model_name,
                "prompt_strategy": prompt_strategy,
                "use_cache": use_cache
            },
            timeout=180
        )

    if response.status_code == 200:
        data = response.json()
        answer = data["response"]["response"]

        st.session_state.messages.append({
            "role": "user",
            "content": query
        })

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

        st.session_state.last_tool_context = data.get("tool_result")

        st.rerun()
    else:
        st.error("Failed to get response from backend.")

if st.session_state.messages:
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    st.markdown("### Conversation")

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div class="user-msg">
                    <div class="meta-text">You</div>
                    {msg["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="assistant-msg">
                    <div class="meta-text">AI Strategy Copilot</div>
                    {msg["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown('</div>', unsafe_allow_html=True)