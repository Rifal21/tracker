import streamlit as st

from components.api import DEFAULT_URL, settings as current


def render():
    st.title("⚙️ Settings")
    url, key = current()
    st.session_state["backend_url"] = st.text_input("URL backend", url or DEFAULT_URL)
    st.session_state["api_key"] = st.text_input("API key", key, type="password")
    st.caption("Disimpan hanya di sesi browser ini.")
