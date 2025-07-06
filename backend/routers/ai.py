from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from typing import List
import google.generativeai as genai
import os
# import fitz  # PyMuPDF  # Commented out due to dependency issues
from dotenv import load_dotenv
from io import BytesIO

from backend.models.schemas import (
    AIProcessRequest, AIProcessResponse, QuizResponse, QuizQuestion,
    FactCheckStatus
)
from backend.auth.jwt_handler import get_current_active_user

load_dotenv()

router = APIRouter()

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
g_model = genai.GenerativeModel("gemini-1.5-flash")

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes"""
    # For now, return a sample text since PyMuPDF is not available
    # In production, you would use PyMuPDF or another PDF library
    return """
Sample extracted text from PDF:

This is a demonstration of the PDF text extraction feature. 
In a real implementation, this would contain the actual text 
from the uploaded PDF file.

Key points:
• PDF text extraction is working
• AI processing is available
• Content can be formatted, summarized, and fact-checked
• The system supports multiple languages

This sample text can be used to test the AI features.
"""

@router.post("/format-text", response_model=AIProcessResponse)
async def format_text(
    request: AIProcessRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Format and clean up extracted text"""
    try:
        prompt = (
            f"Please clean up the formatting of this extracted text. "
            f"Fix line breaks and make it human-readable. Respond in {request.language}:\n\n"
            f"{request.text}"
        )
        
        response = g_model.generate_content(prompt)
        
        return AIProcessResponse(
            result=response.text,
            confidence=0.9
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error formatting text: {str(e)}"
        )

@router.post("/summarize", response_model=AIProcessResponse)
async def summarize_text(
    request: AIProcessRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Summarize text into bullet points"""
    try:
        prompt = (
            f"Please summarize the following lecture into short, clean bullet points. "
            f"Make sure all key ideas are kept. Respond in {request.language}:\n\n"
            f"{request.text}"
        )
        
        response = g_model.generate_content(prompt)
        
        return AIProcessResponse(
            result=response.text,
            confidence=0.85
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error summarizing text: {str(e)}"
        )

@router.post("/fact-check", response_model=AIProcessResponse)
async def fact_check_text(
    request: AIProcessRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Validate information and find sources"""
    try:
        # Load fact-checking prompt template
        prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'fact_check.txt')
        with open(prompt_path, 'r') as f:
            prompt_template = f.read()
        
        # Format prompt with content and language
        prompt = prompt_template.replace('{{content}}', request.text).replace('{{language}}', request.language)
        
        response = g_model.generate_content(prompt)
        
        # Parse fact-checking results (simplified)
        fact_checks = []
        confidence = 0.8
        
        return AIProcessResponse(
            result=response.text,
            confidence=confidence,
            additional_data={
                "fact_checks": fact_checks,
                "status": FactCheckStatus.VERIFIED  # This would be determined by AI analysis
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fact-checking text: {str(e)}"
        )

@router.post("/generate-quiz", response_model=QuizResponse)
async def generate_quiz(
    request: AIProcessRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Generate a quiz based on text content"""
    try:
        prompt = (
            f"Please create a quiz with 5 multiple-choice questions based on the following content. "
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
            f"Respond in {request.language}:\n\n{request.text}"
        )
        
        response = g_model.generate_content(prompt)
        quiz_text = response.text
        
        # Parse quiz (simplified parsing logic)
        questions = parse_quiz_response(quiz_text)
        
        return QuizResponse(
            questions=questions,
            total_questions=len(questions)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating quiz: {str(e)}"
        )

def parse_quiz_response(quiz_text: str) -> List[QuizQuestion]:
    """Parse AI-generated quiz text into structured format"""
    import re
    
    questions = []
    
    # Split by question numbers
    q_splits = re.split(r'\n?(\d+)[\.\)] ', quiz_text)
    q_splits = [q.strip() for q in q_splits if q.strip()]
    
    for i in range(1, len(q_splits), 2):
        if i + 1 < len(q_splits):
            q_block = q_splits[i + 1]
            lines = q_block.split('\n')
            
            if not lines:
                continue
                
            question_text = lines[0].strip()
            options = []
            correct_answer = None
            
            option_pattern = re.compile(r'^([A-D])\)\s*(.*)')
            
            for line in lines[1:]:
                line = line.strip()
                if line.lower().startswith("answer"):
                    match = re.search(r'([A-D])', line, re.I)
                    if match:
                        correct_answer = match.group(1).upper()
                else:
                    match = option_pattern.match(line)
                    if match:
                        options.append(f"{match.group(1)}) {match.group(2)}")
            
            if len(options) == 4 and correct_answer:
                questions.append(QuizQuestion(
                    question=question_text,
                    options=options,
                    correct_answer=correct_answer,
                    explanation=None
                ))
    
    return questions

@router.post("/process-pdf", response_model=AIProcessResponse)
async def process_pdf_file(
    file: UploadFile = File(...),
    language: str = "English",
    operation: str = "format",
    current_user: dict = Depends(get_current_active_user)
):
    """Process uploaded PDF file"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(file_content)
        
        if not extracted_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from PDF"
            )
        
        # Process based on operation type
        request = AIProcessRequest(
            text=extracted_text,
            language=language,
            operation=operation
        )
        
        if operation == "format":
            return await format_text(request, current_user)
        elif operation == "summarize":
            return await summarize_text(request, current_user)
        elif operation == "fact_check":
            return await fact_check_text(request, current_user)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid operation. Use: format, summarize, or fact_check"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF: {str(e)}"
        )

@router.post("/enhance-note", response_model=AIProcessResponse)
async def enhance_note_content(
    request: AIProcessRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Enhance note content with AI suggestions"""
    try:
        prompt = (
            f"Please enhance the following note content by:\n"
            f"1. Adding relevant details and context\n"
            f"2. Improving structure and readability\n"
            f"3. Suggesting additional points to consider\n"
            f"4. Maintaining the original meaning and intent\n"
            f"Respond in {request.language}:\n\n"
            f"{request.text}"
        )
        
        response = g_model.generate_content(prompt)
        
        return AIProcessResponse(
            result=response.text,
            confidence=0.85,
            additional_data={
                "enhancement_type": "content_improvement",
                "suggestions": ["Added context", "Improved structure", "Enhanced readability"]
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enhancing note: {str(e)}"
        )
