import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import os
import uuid
import streamlit.components.v1 as components
import re
import random

# --- Configure Gemini API ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY") or "AIzaSyCSDNEOTdNWtJoik1DnP68tXAWzFTCFk2c")
g_model = genai.GenerativeModel("gemini-1.5-flash")

# --- Functions ---
def extract_text_from_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    return "\n".join([page.get_text() for page in doc])

def format_text(text, language):
    prompt = (
        f"Please clean up the formatting of this extracted text. "
        f"Fix line breaks and make it human-readable. Respond in {language}:\n\n{text}"
    )
    response = g_model.generate_content(prompt)
    return response.text

def summarize_text(text, language):
    prompt = (
        f"Please summarize the following lecture into short, clean bullet points. "
        f"Make sure all key ideas are kept. Respond in {language}:\n\n{text}"
    )
    response = g_model.generate_content(prompt)
    return response.text

def validate_and_find_sources(text, language):
    prompt = (
        f"Please validate the following information. "
        f"Identify if the key points are accurate and provide references or research sources to support them. "
        f"Respond in {language}:\n\n{text}"
    )
    response = g_model.generate_content(prompt)
    return response.text

def generate_quiz(text, language):
    prompt = (
        f"Please create a short quiz with 5 multiple-choice questions based on the following content. "
        f"Each question should have 4 options labeled A), B), C), D). "
        f"Distribute the correct answers randomly — do not always use A). "
        f"At the end of each question, indicate the correct answer clearly in the format 'Answer: X' where X is one letter. "
        f"Format strictly like this:\n\n"
        f"1. Question text?\n"
        f"A) Option A\n"
        f"B) Option B\n"
        f"C) Option C\n"
        f"D) Option D\n"
        f"Answer: B\n\n"
        f"Respond in {language}:\n\n{text}"
    )
    response = g_model.generate_content(prompt)
    return response.text

def copy_button(text_to_copy: str, label: str = "📋 Copy"):
    button_id = str(uuid.uuid4()).replace('-', '')
    js_code = f"""
    <script>
    function copyToClipboard_{button_id}() {{
        const text = `{text_to_copy}`;
        navigator.clipboard.writeText(text);
        const button = document.getElementById('{button_id}');
        button.innerText = "✅ Copied!";
        setTimeout(() => button.innerText = "{label}", 2000);
    }}
    </script>
    <button id="{button_id}" onclick="copyToClipboard_{button_id}()">{label}</button>
    """
    components.html(js_code, height=35)

def parse_quiz(quiz_text):
    q_splits = re.split(r'\n?\d+[\.\)] ', quiz_text)
    q_splits = [q.strip() for q in q_splits if q.strip()]
    parsed = []

    option_pattern = re.compile(r'^([A-D])[\).]\s*(.*)')

    for q_block in q_splits:
        lines = q_block.split('\n')
        question = lines[0].strip()
        options = []
        answer = None

        for line in lines[1:]:
            if line.lower().startswith("answer"):
                m = re.search(r'([A-D])', line, re.I)
                if m:
                    answer = m.group(1).upper()
            else:
                m = option_pattern.match(line.strip())
                if m:
                    options.append((m.group(1), m.group(2)))

        # Find correct text
        correct_text = next((text for label, text in options if label == answer), None)

        # Shuffle options
        random.shuffle(options)

        # Relabel options A-D
        labels = ['A', 'B', 'C', 'D']
        shuffled_options = []
        new_answer = None
        for idx, (old_label, text) in enumerate(options):
            label = labels[idx]
            shuffled_options.append(f"{label}) {text}")
            if text == correct_text:
                new_answer = label

        parsed.append({
            "question": question,
            "options": shuffled_options,
            "answer": new_answer
        })
    return parsed

def show_quiz_with_spoilers(quiz_text):
    parsed_quiz = parse_quiz(quiz_text)
    if not parsed_quiz:
        st.warning("⚠️ Could not parse quiz format. Showing raw quiz text:")
        st.markdown(quiz_text)
        return

    st.markdown("### 🧠 Quiz (Answers Hidden)")

    for i, q in enumerate(parsed_quiz):
        st.markdown(f"**Q{i+1}: {q['question']}**")
        for opt in q["options"]:
            st.markdown(f"- {opt}")
        with st.expander("👀 Show Answer"):
            st.markdown(f"✅ **Answer: {q['answer']})**")
        st.markdown("---")

# --- Streamlit UI ---
st.set_page_config(page_title="PDF Summarizer", layout="centered")
st.title("📄 PDF Formatter + Summarizer with Gemini")

uploaded_file = st.file_uploader("📤 Upload a PDF file", type=["pdf"])

st.markdown("### 🌐 Output Language")
language_choice = st.selectbox("Choose a response language", 
    ["English", "Thai", "Japanese", "Chinese", "Korean", "Spanish", "Other..."]
)
custom_language = ""
if language_choice == "Other...":
    custom_language = st.text_input("Enter your desired language (e.g., French, German, Bahasa Indonesia)")
    language = custom_language.strip() if custom_language.strip() else "English"
else:
    language = language_choice

summarize = st.checkbox("Also summarize after formatting", value=True)

if uploaded_file:
    file_bytes = uploaded_file.read()

    with st.spinner("🔍 Extracting text from PDF..."):
        raw_text = extract_text_from_pdf(file_bytes)

    with st.spinner(f"🧼 Formatting with Gemini ({language})..."):
        formatted = format_text(raw_text, language)

    st.markdown("## 🧾 Formatted Text")
    with st.expander("🔍 View formatted result"):
        st.markdown(formatted, unsafe_allow_html=True)
    copy_button(formatted, label="📋 Copy Formatted")
    st.download_button("💾 Download Formatted Text", formatted, file_name="formatted_text.md")

    summary = None
    if summarize:
        with st.spinner(f"📌 Summarizing in {language}..."):
            summary = summarize_text(formatted, language)

        st.markdown("## 📌 Summary")
        with st.expander("📝 View summary"):
            st.markdown(summary, unsafe_allow_html=True)
        copy_button(summary, label="📋 Copy Summary")
        st.download_button("💾 Download Summary", summary, file_name="summary.md")

        if st.button("🔁 Summarize Again (Simplify Further)"):
            with st.spinner("🌀 Generating simpler summary..."):
                re_summary = summarize_text(summary, language)

            st.markdown("### 🔄 Simpler Summary")
            with st.expander("🧠 View simpler summary"):
                st.markdown(re_summary, unsafe_allow_html=True)
            copy_button(re_summary, label="📋 Copy Simpler Summary")
            st.download_button("💾 Download Simpler Summary", re_summary, file_name="simpler_summary.md")

    text_to_validate = summary if summary else formatted

    if st.button("🔎 Validate & Find Sources"):
        with st.spinner("🔍 Validating information and finding sources..."):
            validation_result = validate_and_find_sources(text_to_validate, language)

        st.markdown("## 🔍 Validation & Supporting Sources")
        with st.expander("🗂️ View validation and sources"):
            st.markdown(validation_result, unsafe_allow_html=True)
        copy_button(validation_result, label="📋 Copy Validation")
        st.download_button("💾 Download Validation & Sources", validation_result, file_name="validation_sources.md")

    if st.button("❓ Generate Quick Quiz"):
        with st.spinner("📝 Creating quiz to test your understanding..."):
            quiz = generate_quiz(text_to_validate, language)

        st.markdown("## ❓ Quick Quiz")
        with st.expander("📝 Take the Quiz"):
            show_quiz_with_spoilers(quiz)

        copy_button(quiz, label="📋 Copy Quiz")
        st.download_button("💾 Download Quiz", quiz, file_name="quiz.md")
