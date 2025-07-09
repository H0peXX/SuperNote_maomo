from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from datetime import datetime

from backend.models.schemas import UserResponse, UserUpdate
from backend.auth.jwt_handler import get_current_active_user
from database.mongodb import get_database

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 10,
    current_user: dict = Depends(get_current_active_user)
):
    """Get list of users (requires authentication)"""
    db = get_database()
    
    cursor = db.users.find(
        {"is_active": True},
        {"hashed_password": 0}  # Exclude password field
    ).skip(skip).limit(limit)
    users = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string
    for user in users:
        user["_id"] = str(user["_id"])
    
    return [UserResponse(**user) for user in users]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get user by ID"""
    db = get_database()
    
    # Validate ObjectId
    try:
        object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    user = await db.users.find_one(
        {"_id": object_id, "is_active": True},
        {"hashed_password": 0}  # Exclude password field
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user["_id"] = str(user["_id"])
    return UserResponse(**user)

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update current user profile"""
    db = get_database()
    
    # Prepare update data
    update_data = {}
    if user_update.username:
        # Check if username is already taken
        existing_user = await db.users.find_one({
            "username": user_update.username,
            "_id": {"$ne": current_user["_id"]}
        })
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        update_data["username"] = user_update.username
    
    if user_update.email:
        # Check if email is already taken
        existing_user = await db.users.find_one({
            "email": user_update.email,
            "_id": {"$ne": current_user["_id"]}
        })
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already taken"
            )
        update_data["email"] = user_update.email
    
    if user_update.full_name:
        update_data["full_name"] = user_update.full_name
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    update_data["updated_at"] = datetime.utcnow()
    
    # Update user
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_data}
    )
    
    # Get updated user
    updated_user = await db.users.find_one(
        {"_id": current_user["_id"]},
        {"hashed_password": 0}
    )
    
    updated_user["_id"] = str(updated_user["_id"])
    return UserResponse(**updated_user)

@router.delete("/me")
async def delete_current_user(
    current_user: dict = Depends(get_current_active_user)
):
    """Deactivate current user account"""
    db = get_database()
    
    # Soft delete - mark as inactive
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "User account deactivated successfully"}

@router.get("/search/", response_model=List[UserResponse])
async def search_users(
    query: str,
    limit: int = 10,
    current_user: dict = Depends(get_current_active_user)
):
    """Search users by username, email, or full name"""
    db = get_database()
    
    # Create search filter
    search_filter = {
        "$and": [
            {"is_active": True},
            {
                "$or": [
                    {"username": {"$regex": query, "$options": "i"}},
                    {"email": {"$regex": query, "$options": "i"}},
                    {"full_name": {"$regex": query, "$options": "i"}}
                ]
            }
        ]
    }
    
    cursor = db.users.find(
        search_filter,
        {"hashed_password": 0}
    ).limit(limit)
    users = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string
    for user in users:
        user["_id"] = str(user["_id"])
    
    return [UserResponse(**user) for user in users]
