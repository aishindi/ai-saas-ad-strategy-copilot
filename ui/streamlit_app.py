import streamlit as st
import requests

st.set_page_config(page_title="AI SaaS Ad Strategy Copilot", layout="wide")

st.title("AI SaaS Ad Strategy Copilot")
st.write("Ask strategic advertising questions for SaaS campaign planning.")

query = st.text_area("Enter your question")
model_name = st.selectbox("Choose model", ["mistral", "llama3"])

if st.button("Submit"):
    if query.strip():
        response = requests.post(
            "http://127.0.0.1:8000/ask",
            json={"query": query, "model_name": model_name},
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            st.subheader("Tool Output")
            st.json(data["tool_result"])

            st.subheader("Assistant Response")
            st.write(data["response"])
        else:
            st.error("Failed to get response from backend.")