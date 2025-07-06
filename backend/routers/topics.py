from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from datetime import datetime

from backend.models.schemas import (
    TopicCreate, TopicUpdate, TopicResponse
)
from backend.auth.jwt_handler import get_current_active_user
from database.mongodb import get_database

router = APIRouter()

async def check_topic_permission(topic_id: str, user_id: str):
    """Check if user has permission to access topic"""
    db = get_database()
    
    try:
        object_id = ObjectId(topic_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid topic ID format"
        )
    
    topic = await db.topics.find_one({"_id": object_id})
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Check if user has access to the team
    team = await db.teams.find_one({"_id": ObjectId(topic["team_id"])})
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated team not found"
        )
    
    # Check if user is owner or member of the team
    if (str(team["owner_id"]) != str(user_id) and 
        not any(str(member["user_id"]) == str(user_id) for member in team.get("members", []))):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not a member of this team"
        )
    
    return topic

@router.post("/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic: TopicCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new topic in a team"""
    db = get_database()
    
    # Verify user has access to the team
    try:
        team_object_id = ObjectId(topic.team_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid team ID format"
        )
    
    team = await db.teams.find_one({"_id": team_object_id})
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if user is owner or member
    if (str(team["owner_id"]) != str(current_user["_id"]) and 
        not any(str(member["user_id"]) == str(current_user["_id"]) for member in team.get("members", []))):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not a member of this team"
        )
    
    # Check if topic name already exists in team
    existing_topic = await db.topics.find_one({
        "team_id": topic.team_id,
        "name": topic.name
    })
    if existing_topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic with this name already exists in the team"
        )
    
    # Create topic
    topic_doc = {
        "name": topic.name,
        "description": topic.description,
        "tags": topic.tags,
        "team_id": topic.team_id,
        "created_by": current_user["_id"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.topics.insert_one(topic_doc)
    topic_doc["_id"] = str(result.inserted_id)
    topic_doc["created_by"] = str(topic_doc["created_by"])
    
    return TopicResponse(**topic_doc)

@router.get("/team/{team_id}", response_model=List[TopicResponse])
async def get_team_topics(
    team_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get all topics for a team"""
    db = get_database()
    
    # Verify user has access to the team
    try:
        team_object_id = ObjectId(team_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid team ID format"
        )
    
    team = await db.teams.find_one({"_id": team_object_id})
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if user is owner or member
    if (str(team["owner_id"]) != str(current_user["_id"]) and 
        not any(str(member["user_id"]) == str(current_user["_id"]) for member in team.get("members", []))):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not a member of this team"
        )
    
    # Get topics
    cursor = db.topics.find({"team_id": team_id})
    topics = await cursor.to_list(length=None)
    
    # Convert ObjectIds to strings
    for topic in topics:
        topic["_id"] = str(topic["_id"])
        topic["created_by"] = str(topic["created_by"])
    
    return [TopicResponse(**topic) for topic in topics]

@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(
    topic_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get topic details"""
    topic = await check_topic_permission(topic_id, current_user["_id"])
    
    topic["_id"] = str(topic["_id"])
    topic["created_by"] = str(topic["created_by"])
    
    return TopicResponse(**topic)

@router.put("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: str,
    topic_update: TopicUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update topic (creator or team admin/owner only)"""
    topic = await check_topic_permission(topic_id, current_user["_id"])
    
    # Check if user is creator, team owner, or team admin
    db = get_database()
    team = await db.teams.find_one({"_id": ObjectId(topic["team_id"])})
    
    is_creator = str(topic["created_by"]) == str(current_user["_id"])
    is_team_owner = str(team["owner_id"]) == str(current_user["_id"])
    is_team_admin = any(
        str(member["user_id"]) == str(current_user["_id"]) and member["role"] == "admin"
        for member in team.get("members", [])
    )
    
    if not (is_creator or is_team_owner or is_team_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Only topic creator or team admins can update topics"
        )
    
    update_data = {}
    if topic_update.name:
        # Check if new name conflicts with existing topics in team
        existing_topic = await db.topics.find_one({
            "team_id": topic["team_id"],
            "name": topic_update.name,
            "_id": {"$ne": ObjectId(topic_id)}
        })
        if existing_topic:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Topic with this name already exists in the team"
            )
        update_data["name"] = topic_update.name
    
    if topic_update.description is not None:
        update_data["description"] = topic_update.description
    
    if topic_update.tags is not None:
        update_data["tags"] = topic_update.tags
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    update_data["updated_at"] = datetime.utcnow()
    
    await db.topics.update_one(
        {"_id": ObjectId(topic_id)},
        {"$set": update_data}
    )
    
    # Get updated topic
    updated_topic = await db.topics.find_one({"_id": ObjectId(topic_id)})
    updated_topic["_id"] = str(updated_topic["_id"])
    updated_topic["created_by"] = str(updated_topic["created_by"])
    
    return TopicResponse(**updated_topic)

@router.delete("/{topic_id}")
async def delete_topic(
    topic_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete topic (creator or team owner only)"""
    topic = await check_topic_permission(topic_id, current_user["_id"])
    
    # Check if user is creator or team owner
    db = get_database()
    team = await db.teams.find_one({"_id": ObjectId(topic["team_id"])})
    
    is_creator = str(topic["created_by"]) == str(current_user["_id"])
    is_team_owner = str(team["owner_id"]) == str(current_user["_id"])
    
    if not (is_creator or is_team_owner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Only topic creator or team owner can delete topics"
        )
    
    # Delete all notes in this topic first
    await db.notes.delete_many({"topic_id": topic_id})
    
    # Delete the topic
    await db.topics.delete_one({"_id": ObjectId(topic_id)})
    
    return {"message": "Topic and associated notes deleted successfully"}

@router.get("/search/{team_id}", response_model=List[TopicResponse])
async def search_topics(
    team_id: str,
    query: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Search topics within a team"""
    db = get_database()
    
    # Verify user has access to the team
    try:
        team_object_id = ObjectId(team_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid team ID format"
        )
    
    team = await db.teams.find_one({"_id": team_object_id})
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if user is owner or member
    if (str(team["owner_id"]) != str(current_user["_id"]) and 
        not any(str(member["user_id"]) == str(current_user["_id"]) for member in team.get("members", []))):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not a member of this team"
        )
    
    # Search topics
    search_filter = {
        "team_id": team_id,
        "$or": [
            {"name": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
            {"tags": {"$in": [{"$regex": query, "$options": "i"}]}}
        ]
    }
    
    cursor = db.topics.find(search_filter)
    topics = await cursor.to_list(length=None)
    
    # Convert ObjectIds to strings
    for topic in topics:
        topic["_id"] = str(topic["_id"])
        topic["created_by"] = str(topic["created_by"])
    
    return [TopicResponse(**topic) for topic in topics]
