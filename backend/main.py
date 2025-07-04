from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from PIL import Image
from pdf2image import convert_from_bytes
import io

# === ตั้งค่า Gemini API ===
genai.configure(api_key=os.getenv("GEMINI_API_KEY") or "AIzaSyCSDNEOTdNWtJoik1DnP68tXAWzFTCFk2c")
text_model = genai.GenerativeModel("gemini-1.5-flash")

# === FastAPI App ===
app = FastAPI()

# === Middleware (CORS) ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # สำหรับ dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Models สำหรับ format / summarize ===
class FormatRequest(BaseModel):
    text: str
    language: str = "English"

class SummaryRequest(BaseModel):
    text: str
    language: str = "English"

# === Endpoint: /upload/ สำหรับ PDF โดยใช้ Gemini Vision ===
@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        pdf_bytes = await file.read()
        images = convert_from_bytes(pdf_bytes)

        combined_text = ""
        for i, img in enumerate(images):
            prompt = f"Extract all readable text from page {i+1}."
            result = text_model.generate_content([prompt, img])
            combined_text += f"\n\n--- Page {i+1} ---\n{result.text}"

        return {"original_text": combined_text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF OCR failed: {str(e)}")

# === Endpoint: /ocr/ สำหรับรูปภาพ โดยใช้ Gemini Vision ===
@app.post("/ocr/")
async def ocr_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        prompt = "Extract all readable text from this image."
        result = text_model.generate_content([prompt, image])

        return {"text": result.text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image OCR failed: {str(e)}")

# === Endpoint: /format/ → ใช้ Gemini 1.5 Flash จัดรูปแบบ ===
@app.post("/format/")
def format_text(req: FormatRequest):
    try:
        prompt = f"Please clean up formatting. Respond in {req.language}:\n\n{req.text}"
        result = text_model.generate_content(prompt)
        return {"formatted_text": result.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Formatting failed: {str(e)}")

# === Endpoint: /summarize/ → ใช้ Gemini 1.5 Flash สรุป ===
@app.post("/summarize/")
def summarize_text(req: SummaryRequest):
    try:
        prompt = f"Summarize in bullet points. Respond in {req.language}:\n\n{req.text}"
        result = text_model.generate_content(prompt)
        return {"summary": result.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")
