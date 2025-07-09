from fastapi import APIRouter, HTTPException, status, Depends, WebSocket, WebSocketDisconnect
from typing import List
from datetime import datetime
from bson import ObjectId
from loguru import logger

from backend.models.schemas import NoteCreate, NoteUpdate, NoteResponse, FactCheckStatus, Comment, NoteVersion
from backend.auth.jwt_handler import get_current_active_user
from database.mongodb import get_database

router = APIRouter()

async def check_note_permission(note_id: str, user_id: str):
    """Check if user has permission to access/edit note"""
    db = get_database()
    
    try:
        object_id = ObjectId(note_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid note ID format"
        )
    
    note = await db.notes.find_one({"_id": object_id})
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Check if user is creator or collaborator
    if (str(note["created_by"]) != str(user_id) and 
        str(user_id) not in note.get("collaborators", [])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not authorized to access this note"
        )
    
    return note

@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note: NoteCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new note under a topic"""
    db = get_database()
    
    # Validate topic ownership
    topic = await db.topics.find_one({"_id": ObjectId(note.topic_id), "created_by": current_user["_id"]})
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid topic ID or access denied"
        )
    
    # Create note
    note_doc = {
        "title": note.title,
        "content": note.content,
        "topic_id": note.topic_id,
        "team_id": topic["team_id"],
        "created_by": current_user["_id"],
        "collaborators": [],
        "fact_checks": [],
        "comments": [],
        "versions": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.notes.insert_one(note_doc)
    note_doc["_id"] = str(result.inserted_id)
    note_doc["created_by"] = str(note_doc["created_by"])
    
    return NoteResponse(**note_doc)

@router.get("/", response_model=List[NoteResponse])
async def get_topic_notes(
    topic_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get all notes under a topic"""
    db = get_database()
    
    cursor = db.notes.find({"topic_id": topic_id})
    notes = await cursor.to_list(length=None)
    
    # Convert ObjectIds to strings
    for note in notes:
        note["_id"] = str(note["_id"])
        note["created_by"] = str(note["created_by"])
    
    return [NoteResponse(**note) for note in notes]

@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get note details"""
    note = await check_note_permission(note_id, current_user["_id"])
    
    note["_id"] = str(note["_id"])
    note["created_by"] = str(note["created_by"])
    
    return NoteResponse(**note)

@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    note_update: NoteUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update note contents (creator or collaborator only)"""
    note = await check_note_permission(note_id, current_user["_id"])
    
    update_data = {}
    if note_update.title:
        update_data["title"] = note_update.title
    if note_update.content is not None:
        update_data["content"] = note_update.content
    if note_update.status is not None:
        update_data["status"] = note_update.status
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    update_data["updated_at"] = datetime.utcnow()
    
    db = get_database()
    await db.notes.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": update_data}
    )
    
    # Get updated note
    updated_note = await db.notes.find_one({"_id": ObjectId(note_id)})
    updated_note["_id"] = str(updated_note["_id"])
    updated_note["created_by"] = str(updated_note["created_by"])
    
    return NoteResponse(**updated_note)

@router.delete("/{note_id}")
async def delete_note(
    note_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete note (creator only)"""
    note = await check_note_permission(note_id, current_user["_id"])
    
    # Only creator can delete
    if str(note["created_by"]) != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Only creator can delete the note"
        )
    
    db = get_database()
    await db.notes.delete_one({"_id": ObjectId(note_id)})
    
    return {"message": "Note deleted successfully"}

@router.post("/{note_id}/collaborators/{user_id}")
async def add_collaborator(
    note_id: str,
    user_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Add collaborator to note"""
    note = await check_note_permission(note_id, current_user["_id"])
    
    # Only creator can add collaborators
    if str(note["created_by"]) != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Only creator can add collaborators"
        )
    
    if user_id in note.get("collaborators", []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a collaborator"
        )
    
    db = get_database()
    await db.notes.update_one(
        {"_id": ObjectId(note_id)},
        {
            "$push": {"collaborators": user_id},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return {"message": "Collaborator added successfully"}

@router.post("/{note_id}/fact-checks")
async def fact_check_note(
    note_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Fact-check note content using AI"""
    note = await check_note_permission(note_id, current_user["_id"])
    
    if not note.get("content"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Note has no content to fact-check"
        )
    
    # Import AI processing
    import google.generativeai as genai
    import os
    
    try:
        # Configure AI if not already done
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI service not available - API key not configured"
            )
        
        genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Create fact-checking prompt
        prompt = f"""
Please fact-check the following content and provide:
1. Overall accuracy assessment (VERIFIED, QUESTIONABLE, or INACCURATE)
2. Specific claims that need verification
3. Sources or references where possible
4. Confidence level (0-100%)

Content to fact-check:
{note['content']}

Respond in JSON format:
{{
  "overall_status": "VERIFIED|QUESTIONABLE|INACCURATE",
  "confidence": 85,
  "claims": [
    {{
      "claim": "specific claim text",
      "status": "VERIFIED|QUESTIONABLE|INACCURATE",
      "explanation": "why this claim is accurate/questionable/inaccurate",
      "sources": ["source1", "source2"]
    }}
  ],
  "summary": "overall summary of fact-check results"
}}
"""
        
        response = model.generate_content(prompt)
        ai_result = response.text
        
        # Try to parse JSON response, fallback to text if parsing fails
        try:
            import json
            fact_check_data = json.loads(ai_result.strip().replace('```json', '').replace('```', ''))
            overall_status = fact_check_data.get('overall_status', 'QUESTIONABLE')
            confidence = fact_check_data.get('confidence', 75)
            summary = fact_check_data.get('summary', ai_result)
        except:
            # Fallback to simple parsing
            overall_status = "QUESTIONABLE"
            confidence = 75
            summary = ai_result
            if "VERIFIED" in ai_result.upper():
                overall_status = "VERIFIED"
                confidence = 85
            elif "INACCURATE" in ai_result.upper():
                overall_status = "INACCURATE"
                confidence = 90
        
        # Create fact-check record
        fact_check = {
            "id": str(ObjectId()),
            "claim": "Overall content accuracy",
            "status": overall_status.lower(),
            "explanation": summary,
            "sources": [],
            "confidence": confidence / 100.0,
            "checked_at": datetime.utcnow(),
            "checked_by": current_user["_id"]
        }
        
        # Update note with fact-check result
        db = get_database()
        await db.notes.update_one(
            {"_id": ObjectId(note_id)},
            {
                "$push": {"fact_checks": fact_check},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return {
            "message": "Fact-check completed successfully",
            "status": overall_status.lower(),
            "confidence": confidence,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during fact-checking: {str(e)}"
        )

@router.delete("/{note_id}/collaborators/{user_id}")
async def remove_collaborator(
    note_id: str,
    user_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Remove collaborator from note (creator or self)"""
    note = await check_note_permission(note_id, current_user["_id"])
    
    # Only creator or self can remove collaborator
    if (str(note["created_by"]) != str(current_user["_id"]) and 
        str(user_id) != str(current_user["_id"])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Only creator or self can remove collaborator"
        )
    
    db = get_database()
    await db.notes.update_one(
        {"_id": ObjectId(note_id)},
        {
            "$pull": {"collaborators": user_id},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return {"message": "Collaborator removed successfully"}

@router.websocket("/ws/{note_id}")
async def note_websocket_endpoint(websocket: WebSocket, note_id: str, token: str):
    """WebSocket endpoint for real-time note collaboration"""
    await websocket.accept()
    db = get_database()
    
    # TODO: Verify token and user
    # NOTE: This is a mock implementation for demonstration purposes
    connected_users = []
    
    try:
        connected_users.append(websocket)
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received: {data}")
            # Echo message to all connected users
            for user in connected_users:
                await user.send_text(data)
    except WebSocketDisconnect:
        connected_users.remove(websocket)
        logger.info("Client disconnected")

@router.post("/{note_id}/comments", response_model=Comment)
async def add_comment(
    note_id: str,
    content: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Add comment to note"""
    note = await check_note_permission(note_id, current_user["_id"])
    
    # Create comment
    comment = Comment(
        id=str(ObjectId()),
        user_id=str(current_user["_id"]),
        content=content,
        created_at=datetime.utcnow()
    )
    
    db = get_database()
    await db.notes.update_one(
        {"_id": ObjectId(note_id)},
        {
            "$push": {"comments": comment.dict()},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return comment

@router.get("/{note_id}/comments", response_model=List[Comment])
async def get_note_comments(
    note_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get comments for note"""
    note = await check_note_permission(note_id, current_user["_id"])
    
    return note.get("comments", [])

@router.post("/{note_id}/fact-checks", response_model=NoteResponse)
async def add_fact_check(
    note_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Add fact-check to note"""
    note = await check_note_permission(note_id, current_user["_id"])
    
    # Mocked AI fact-checking result
    fact_check_result = {
        "claim": "Example claim",
        "status": FactCheckStatus.VERIFIED,
        "explanation": "This claim is verified based on ...",
        "sources": ["Source 1", "Source 2"],
        "confidence": 0.95
    }
    
    db = get_database()
    await db.notes.update_one(
        {"_id": ObjectId(note_id)},
        {
            "$push": {"fact_checks": fact_check_result},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    updated_note = await db.notes.find_one({"_id": ObjectId(note_id)})
    updated_note["_id"] = str(updated_note["_id"])
    updated_note["created_by"] = str(updated_note["created_by"])
    
    return NoteResponse(**updated_note)

