import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import os
import uuid
import streamlit.components.v1 as components
import re
import requests


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
        f"At the end of each question, indicate the correct answer as 'Answer: X' where X is the letter. "
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


# --- Small Inline Copy Button ---
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

# --- Quiz Parsing and Interactive UI ---
def parse_quiz(quiz_text):
    """
    Parse multiple-choice quiz from text.
    Format example:

    1. What is X?
    A) Option 1
    B) Option 2
    C) Option 3
    D) Option 4
    Answer: B

    Returns list of dict with question, options, answer letter.
    """
    # Split questions by numbers + dot/paren (e.g., "1." or "1)")
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
                    options.append(f"{m.group(1)}) {m.group(2)}")

        parsed.append({
            "question": question,
            "options": options,
            "answer": answer
        })
    return parsed

def show_interactive_quiz(quiz_text):
    parsed_quiz = parse_quiz(quiz_text)
    if not parsed_quiz:
        st.write("⚠️ Could not parse quiz format for interactive mode. Showing raw quiz text:")
        st.markdown(quiz_text)
        return

    st.write("Answer the questions and submit to check your answers:")

    user_answers = {}
    for i, q in enumerate(parsed_quiz):
        st.markdown(f"**Q{i+1}: {q['question']}**")
        if q['options']:
            key = f"q{i}"
            user_answers[key] = st.radio("Choose your answer:", q['options'], key=key)
        else:
            st.error("No options found for this question, cannot display interactive quiz.")
            return
        st.write("")

    if st.button("Submit Answers"):
        score = 0
        total = len(parsed_quiz)
        st.markdown("---")
        for i, q in enumerate(parsed_quiz):
            user_key = f"q{i}"
            user_answer = user_answers.get(user_key, "").strip()
            correct_answer = q['answer']

            st.markdown(f"**Q{i+1}: {q['question']}**")

            if user_answer:
                user_letter = user_answer[0]
                if correct_answer and user_letter.upper() == correct_answer:
                    st.success(f"✅ Correct! You chose {user_letter}")
                    score += 1
                else:
                    st.error(f"❌ Wrong! You chose {user_letter}. Correct answer: {correct_answer}")
            else:
                st.warning("You did not select an answer.")

        st.markdown(f"### Your Score: {score} / {total}")

# --- Streamlit UI ---
st.set_page_config(page_title="PDF Summarizer", layout="centered")
st.title("📄 PDF Formatter + Summarizer with Gemini")

# Upload PDF
uploaded_file = st.file_uploader("📤 Upload a PDF file", type=["pdf"])

if uploaded_file:
    file_bytes = uploaded_file.read()
    
    if not file_bytes:
        st.error("❌ Uploaded file is empty. Please upload a valid PDF.")
        st.stop()  # ❗ หยุดการประมวลผลทันที

# Language selector
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

# --- Processing PDF ---
if uploaded_file:
    file_bytes = uploaded_file.read()

       # ✅ ป้องกันไฟล์ว่าง
    if not file_bytes:
        st.error("❌ Uploaded file is empty. Please upload a valid PDF.")
        st.stop()

    with st.spinner("🔍 Extracting text from PDF..."):
        raw_text = extract_text_from_pdf(file_bytes)

    with st.spinner("🔍 Extracting text from PDF..."):
        raw_text = extract_text_from_pdf(file_bytes)

    with st.spinner(f"🧼 Formatting with Gemini ({language})..."):
        formatted = format_text(raw_text, language)

    # --- Formatted Output ---
    st.markdown("## 🧾 Formatted Text")
    with st.expander("🔍 View formatted result"):
        st.markdown(formatted, unsafe_allow_html=True)
    copy_button(formatted, label="📋 Copy Formatted")
    st.download_button("💾 Download Formatted Text", formatted, file_name="formatted_text.md")

    # --- Summary Output ---
    summary = None
    if summarize:
        with st.spinner(f"📌 Summarizing in {language}..."):
            summary = summarize_text(formatted, language)
            # ✅ ส่งข้อมูลไป backend
            res = requests.post("http://localhost:8000/pdfs/", json={
            "file_name": uploaded_file.name,
            "original_text": raw_text,
            "summary": summary
            })

        if res.status_code == 200:
            st.success("✅ PDF saved to database!")
        else:
            st.error(f"❌ Failed to save to backend: {res.status_code} - {res.text}")


        st.markdown("## 📌 Summary")
        with st.expander("📝 View summary"):
            st.markdown(summary, unsafe_allow_html=True)
        copy_button(summary, label="📋 Copy Summary")
        st.download_button("💾 Download Summary", summary, file_name="summary.md")

        # --- Iterative Summary ---
        if st.button("🔁 Summarize Again (Simplify Further)"):
            with st.spinner("🌀 Generating simpler summary..."):
                re_summary = summarize_text(summary, language)

            st.markdown("### 🔄 Simpler Summary")
            with st.expander("🧠 View simpler summary"):
                st.markdown(re_summary, unsafe_allow_html=True)
            copy_button(re_summary, label="📋 Copy Simpler Summary")
            st.download_button("💾 Download Simpler Summary", re_summary, file_name="simpler_summary.md")

    # --- Validation & Sources ---
    text_to_validate = summary if summary else formatted

    if st.button("🔎 Validate & Find Sources"):
        with st.spinner("🔍 Validating information and finding sources..."):
            validation_result = validate_and_find_sources(text_to_validate, language)

        st.markdown("## 🔍 Validation & Supporting Sources")
        with st.expander("🗂️ View validation and sources"):
            st.markdown(validation_result, unsafe_allow_html=True)
        copy_button(validation_result, label="📋 Copy Validation")
        st.download_button("💾 Download Validation & Sources", validation_result, file_name="validation_sources.md")

    # --- Quiz Generation & Interactive Display ---
    if st.button("❓ Generate Quick Quiz"):
        with st.spinner("📝 Creating quiz to test your understanding..."):
            quiz = generate_quiz(text_to_validate, language)

        st.markdown("## ❓ Quick Quiz")
        with st.expander("📝 View quiz"):
            # Show interactive quiz with parsing and radio buttons
            show_interactive_quiz(quiz)

        copy_button(quiz, label="📋 Copy Quiz")
        st.download_button("💾 Download Quiz", quiz, file_name="quiz.md")

API_URL = "http://localhost:8000"  # ปรับตามที่คุณรัน FastAPI

def upload_to_backend(file_name, original_text, summary):
    data = {
        "file_name": file_name,
        "original_text": original_text,
        "summary": summary,
    }
    res = requests.post(f"{API_URL}/pdfs/", json=data)
    return res

def list_all_pdfs():
    res = requests.get(f"{API_URL}/pdfs/")
    if res.status_code == 200:
        return res.json()
    return []

def delete_pdf(pdf_id):
    return requests.delete(f"{API_URL}/pdfs/{pdf_id}")

if uploaded_file:
    file_bytes = uploaded_file.read()

    # ✅ ตรวจว่าไม่ว่าง
    if not file_bytes:
        st.error("❌ Uploaded file is empty. Please upload a valid PDF.")
        st.stop()

    # ✅ OCR
    with st.spinner("🔍 Extracting text from PDF..."):
        raw_text = extract_text_from_pdf(file_bytes)

    # ✅ Formatting
    with st.spinner("🧼 Formatting..."):
        formatted = format_text(raw_text, language)

    # ✅ Summary
    if summarize:
        with st.spinner("📌 Summarizing..."):
            summary = summarize_text(formatted, language)

    # ✅ ส่งเข้า backend
    if st.button("💾 Save to Database"):
        payload = {
            "file_name": uploaded_file.name,
            "original_text": raw_text,
            "summary": summary or ""
        }
        res = requests.post("http://localhost:8000/pdfs/", json=payload)
        if res.status_code == 200:
            st.success("✅ Saved to database")
        else:
            st.error("❌ Save failed")


st.markdown("---")
st.markdown("## 📚 Your Uploaded PDFs")

pdfs = list_all_pdfs()
if not pdfs:
    st.info("No PDFs found.")
else:
    for pdf in pdfs:
        with st.expander(f"📄 {pdf['file_name']}"):
            st.markdown(f"📝 **Original Text**")
            st.text_area("Original", pdf["original_text"], height=150)
            st.markdown(f"📌 **Summary**")
            st.text_area("Summary", pdf["summary"], height=150)

            if st.button("🗑️ Delete", key=pdf["id"]):
                del_res = delete_pdf(pdf["id"])
                if del_res.status_code == 200:
                    st.success("Deleted successfully.")
                    st.rerun()
                else:
                    st.error("Failed to delete.")


