from fastapi import FastAPI, HTTPException
from sqlmodel import select
from models import PDFFile
from database import get_session, init_db
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
import os
import google.generativeai as genai

# --- Configure Gemini API ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY") or "your-api-key")
g_model = genai.GenerativeModel("gemini-1.5-flash")

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

# 🔒 Mock user ID (ไม่มีระบบ login)
MOCK_USER_ID = uuid.UUID("12345678-1234-5678-1234-567812345678")

# 📥 Schema: ใช้ตอนรับ input จาก Streamlit (Create)
class PDFInput(BaseModel):
    file_name: str
    original_text: str
    summary: str

# 🛠 Schema: ใช้ตอน Update (Partial update)
class PDFUpdate(BaseModel):
    file_name: Optional[str] = None
    original_text: Optional[str] = None
    summary: Optional[str] = None

# ✅ CREATE PDF
@app.post("/pdfs/")
def create_pdf(data: PDFInput):
    try:
        pdf = PDFFile(
            id=uuid.uuid4(),
            user_id=MOCK_USER_ID,
            file_name=data.file_name,
            original_text=data.original_text,
            summary=data.summary,
            created_at=datetime.utcnow()
        )
        with get_session() as session:
            session.add(pdf)
            session.commit()
            session.refresh(pdf)
        return pdf
    except Exception as e:
        raise HTTPException(status_code=500, detail="Create failed: " + str(e))

# 📃 READ all PDFs for this user
@app.get("/pdfs/")
def list_pdfs():
    with get_session() as session:
        return session.exec(select(PDFFile).where(PDFFile.user_id == MOCK_USER_ID)).all()

# 📄 READ single PDF
@app.get("/pdfs/{pdf_id}")
def get_pdf(pdf_id: str):
    with get_session() as session:
        pdf = session.get(PDFFile, uuid.UUID(pdf_id))
        if not pdf or pdf.user_id != MOCK_USER_ID:
            raise HTTPException(status_code=404, detail="PDF not found")
        return pdf

# ✏️ UPDATE PDF (file name, text, summary)
@app.put("/pdfs/{pdf_id}/update")
def update_pdf(pdf_id: str, update: PDFUpdate):
    with get_session() as session:
        pdf = session.get(PDFFile, uuid.UUID(pdf_id))
        if not pdf or pdf.user_id != MOCK_USER_ID:
            raise HTTPException(status_code=404, detail="PDF not found")

        if update.file_name is not None:
            pdf.file_name = update.file_name
        if update.original_text is not None:
            pdf.original_text = update.original_text
        if update.summary is not None:
            pdf.summary = update.summary

        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        return pdf

# 🔁 RESUMMARIZE using Gemini again
@app.put("/pdfs/{pdf_id}")
def resummarize_pdf(pdf_id: str):
    with get_session() as session:
        pdf = session.get(PDFFile, uuid.UUID(pdf_id))
        if not pdf or pdf.user_id != MOCK_USER_ID:
            raise HTTPException(status_code=404, detail="PDF not found")

        try:
            prompt = (
                f"Please summarize the following content into short bullet points:\n\n{pdf.original_text}"
            )
            result = g_model.generate_content(prompt)
            pdf.summary = result.text
            session.add(pdf)
            session.commit()
            return {"updated_summary": result.text}
        except Exception as e:
            raise HTTPException(status_code=500, detail="Gemini summarization failed: " + str(e))

# ❌ DELETE PDF
@app.delete("/pdfs/{pdf_id}")
def delete_pdf(pdf_id: str):
    with get_session() as session:
        pdf = session.get(PDFFile, uuid.UUID(pdf_id))
        if not pdf or pdf.user_id != MOCK_USER_ID:
            raise HTTPException(status_code=404, detail="PDF not found")
        session.delete(pdf)
        session.commit()
        return {"deleted": str(pdf.id)}
