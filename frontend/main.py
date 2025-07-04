import streamlit as st
import requests
from PIL import Image
import io

API_URL = "http://localhost:8000"

st.title("📄 Moamo Universal File Processor (Frontend)")

# --- Session State ---
if "original_text" not in st.session_state:
    st.session_state.original_text = ""
if "formatted_text" not in st.session_state:
    st.session_state.formatted_text = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""

# --- Language Selection ---
language = st.selectbox("Language", ["English", "Thai", "Japanese", "Other"])
custom_lang = st.text_input("Custom Language") if language == "Other" else ""
language = custom_lang if custom_lang else language

# --- File Upload ---
uploaded_file = st.file_uploader("📤 Upload PDF or Image", type=["pdf", "jpg", "jpeg", "png", "heic", "webp"])

if uploaded_file and st.session_state.original_text == "":
    file_type = uploaded_file.type

    if file_type == "application/pdf":
        with st.spinner("📄 Uploading and extracting PDF text..."):
            res = requests.post(f"{API_URL}/upload/", files={"file": uploaded_file})
            if res.status_code != 200:
                st.error("❌ Upload failed")
            else:
                st.session_state.original_text = res.json()["original_text"]

    elif file_type.startswith("image/"):
        with st.spinner("🖼️ Uploading image and running OCR..."):
            res = requests.post(f"{API_URL}/ocr/", files={"file": uploaded_file})
            if res.status_code != 200:
                st.error("❌ OCR failed")
            else:
                st.session_state.original_text = res.json()["text"]

    else:
        st.error("❌ Unsupported file type.")

# --- Format Text ---
if st.session_state.original_text and st.session_state.formatted_text == "":
    with st.spinner("✨ Formatting text..."):
        res_fmt = requests.post(
            f"{API_URL}/format/",
            json={"text": st.session_state.original_text, "language": language}
        )
        if res_fmt.status_code == 200:
            st.session_state.formatted_text = res_fmt.json()["formatted_text"]
        else:
            st.error("❌ Formatting failed")

# --- Show Formatted Text ---
if st.session_state.formatted_text:
    st.subheader("🧾 Formatted Text")
    st.markdown(st.session_state.formatted_text)

# --- Summarize Button ---
if st.session_state.formatted_text:
    if st.button("📌 Summarize"):
        with st.spinner("🧠 Summarizing..."):
            res_sum = requests.post(
                f"{API_URL}/summarize/",
                json={"text": st.session_state.formatted_text, "language": language}
            )
            if res_sum.status_code == 200:
                st.session_state.summary = res_sum.json()["summary"]
            else:
                st.error("❌ Summary failed")

# --- Show Summary ---
if st.session_state.summary:
    st.subheader("📌 Summary")
    st.markdown(st.session_state.summary)

# --- Reset Button ---
if st.button("🔄 Reset"):
    st.session_state.original_text = ""
    st.session_state.formatted_text = ""
    st.session_state.summary = ""
    st.experimental_rerun()
