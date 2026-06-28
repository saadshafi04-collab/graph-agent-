import streamlit as st
import base64
import os
from dotenv import load_dotenv
from model import init_db
from agent import run_agent

load_dotenv("graph_agent/.env")
api_key = os.getenv("ANTHROPIC_API_KEY")

init_db()

st.title("Asset Monitoring Agent")

if "history" not in st.session_state:
    st.session_state.history = []
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        for chart in msg.get("charts", []):
            st.image(base64.b64decode(chart))

prompt = st.chat_input("Ask about your assets...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt, "charts": []})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Thinking..."):
        result = run_agent(prompt, st.session_state.history, api_key)

    with st.chat_message("assistant"):
        st.markdown(result["text"])
        for chart in result["charts"]:
            st.image(base64.b64decode(chart))

    st.session_state.messages.append({"role": "assistant", "content": result["text"], "charts": result["charts"]})
