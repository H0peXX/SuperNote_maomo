from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import fitz  # PyMuPDF
import google.generativeai as genai
import os

# -- API KEY --
genai.configure(api_key=os.getenv("GEMINI_API_KEY") or "AIzaSyCSDNEOTdNWtJoik1DnP68tXAWzFTCFk2c")
g_model = genai.GenerativeModel("gemini-1.5-flash")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ปรับตอน deploy จริง
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FormatRequest(BaseModel):
    text: str
    language: str = "English"

class SummaryRequest(BaseModel):
    text: str
    language: str = "English"

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        doc = fitz.open(stream=contents, filetype="pdf")
        text = "\n".join([page.get_text() for page in doc])
        return {"original_text": text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF reading failed: {str(e)}")

@app.post("/format/")
def format_text(req: FormatRequest):
    try:
        prompt = f"Please clean up formatting. Respond in {req.language}:\n\n{req.text}"
        result = g_model.generate_content(prompt)
        return {"formatted_text": result.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Formatting failed: {str(e)}")

@app.post("/summarize/")
def summarize_text(req: SummaryRequest):
    try:
        prompt = f"Summarize in bullet points. Respond in {req.language}:\n\n{req.text}"
        result = g_model.generate_content(prompt)
        return {"summary": result.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")
