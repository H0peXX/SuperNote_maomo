### 📁 backend/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import fitz  # PyMuPDF
import google.generativeai as genai
import os

# --- Configure Gemini API ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY") or "your-api-key")
g_model = genai.GenerativeModel("gemini-1.5-flash")

app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class FormatRequest(BaseModel):
    text: str
    language: str = "English"

class SummaryRequest(BaseModel):
    text: str
    language: str = "English"

# --- Endpoints ---

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        doc = fitz.open(stream=contents, filetype="pdf")
        text = "\n".join([page.get_text() for page in doc])
        return {"original_text": text}
    except Exception as e:
        raise HTTPException(status_code=400, detail="PDF reading failed")


@app.post("/format/")
def format_text(req: FormatRequest):
    prompt = (
        f"Please clean up the formatting of this extracted text. "
        f"Fix line breaks and make it human-readable. Respond in {req.language}:\n\n{req.text}"
    )
    result = g_model.generate_content(prompt)
    return {"formatted_text": result.text}


@app.post("/summarize/")
def summarize_text(req: SummaryRequest):
    prompt = (
        f"Please summarize the following lecture into short, clean bullet points. "
        f"Make sure all key ideas are kept. Respond in {req.language}:\n\n{req.text}"
    )
    result = g_model.generate_content(prompt)
    return {"summary": result.text}
