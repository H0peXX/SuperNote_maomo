### ✅ FRONTEND (streamlit/main.py)

import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("📄 Moamo PDF Processor (Frontend)")

uploaded_file = st.file_uploader("📤 Upload PDF")

language = st.selectbox("Language", ["English", "Thai", "Japanese", "Other"])
custom_lang = st.text_input("Custom Language") if language == "Other" else ""
language = custom_lang if custom_lang else language

if uploaded_file:
    st.info("Uploading and extracting text...")
    res = requests.post(f"{API_URL}/upload/", files={"file": uploaded_file})
    if res.status_code != 200:
        st.error("❌ Upload failed")
    else:
        original_text = res.json()["original_text"]

        # Format
        st.info("Formatting text...")
        res_fmt = requests.post(f"{API_URL}/format/", json={"text": original_text, "language": language})
        formatted_text = res_fmt.json()["formatted_text"]
        st.subheader("🧾 Formatted Text")
        st.markdown(formatted_text)

        # Summarize
        if st.button("📌 Summarize"):
            st.info("Generating summary...")
            res_sum = requests.post(f"{API_URL}/summarize/", json={"text": formatted_text, "language": language})
            summary = res_sum.json()["summary"]
            st.subheader("📌 Summary")
            st.markdown(summary)
