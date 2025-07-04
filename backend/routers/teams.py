from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from datetime import datetime

from models.schemas import (
    TeamCreate, TeamUpdate, TeamResponse, TeamInvitation, 
    TeamRole, TeamMember
)
from auth.jwt_handler import get_current_active_user
from database.mongodb import get_database

router = APIRouter()

async def check_team_permission(team_id: str, user_id: str, required_roles: List[TeamRole] = None):
    """Check if user has permission to access team"""
    db = get_database()
    
    try:
        object_id = ObjectId(team_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid team ID format"
        )
    
    team = await db.teams.find_one({"_id": object_id})
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if user is owner
    if str(team["owner_id"]) == str(user_id):
        return team
    
    # Check if user is member
    user_member = None
    for member in team.get("members", []):
        if str(member["user_id"]) == str(user_id):
            user_member = member
            break
    
    if not user_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not a member of this team"
        )
    
    # Check role requirements
    if required_roles and user_member["role"] not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Insufficient permissions"
        )
    
    return team

@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team: TeamCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new team"""
    db = get_database()
    
    team_doc = {
        "name": team.name,
        "description": team.description,
        "owner_id": current_user["_id"],
        "members": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.teams.insert_one(team_doc)
    team_doc["_id"] = str(result.inserted_id)
    team_doc["owner_id"] = str(team_doc["owner_id"])
    
    return TeamResponse(**team_doc)

@router.get("/", response_model=List[TeamResponse])
async def get_user_teams(
    current_user: dict = Depends(get_current_active_user)
):
    """Get teams where user is owner or member"""
    db = get_database()
    
    # Find teams where user is owner or member
    teams = await db.teams.find({
        "$or": [
            {"owner_id": current_user["_id"]},
            {"members.user_id": current_user["_id"]}
        ]
    }).to_list(length=None)
    
    # Convert ObjectIds to strings
    for team in teams:
        team["_id"] = str(team["_id"])
        team["owner_id"] = str(team["owner_id"])
        for member in team.get("members", []):
            member["user_id"] = str(member["user_id"])
    
    return [TeamResponse(**team) for team in teams]

@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get team details"""
    team = await check_team_permission(team_id, current_user["_id"])
    
    team["_id"] = str(team["_id"])
    team["owner_id"] = str(team["owner_id"])
    for member in team.get("members", []):
        member["user_id"] = str(member["user_id"])
    
    return TeamResponse(**team)

@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    team_update: TeamUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update team (owner or admin only)"""
    team = await check_team_permission(
        team_id, current_user["_id"], 
        [TeamRole.OWNER, TeamRole.ADMIN]
    )
    
    update_data = {}
    if team_update.name:
        update_data["name"] = team_update.name
    if team_update.description is not None:
        update_data["description"] = team_update.description
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    update_data["updated_at"] = datetime.utcnow()
    
    db = get_database()
    await db.teams.update_one(
        {"_id": ObjectId(team_id)},
        {"$set": update_data}
    )
    
    # Get updated team
    updated_team = await db.teams.find_one({"_id": ObjectId(team_id)})
    updated_team["_id"] = str(updated_team["_id"])
    updated_team["owner_id"] = str(updated_team["owner_id"])
    for member in updated_team.get("members", []):
        member["user_id"] = str(member["user_id"])
    
    return TeamResponse(**updated_team)

@router.delete("/{team_id}")
async def delete_team(
    team_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete team (owner only)"""
    team = await check_team_permission(team_id, current_user["_id"])
    
    # Only owner can delete team
    if str(team["owner_id"]) != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team owner can delete the team"
        )
    
    db = get_database()
    
    # Also delete all related notes and topics
    await db.notes.delete_many({"team_id": team_id})
    await db.topics.delete_many({"team_id": team_id})
    await db.teams.delete_one({"_id": ObjectId(team_id)})
    
    return {"message": "Team deleted successfully"}

@router.post("/{team_id}/invite")
async def invite_user_to_team(
    team_id: str,
    invitation: TeamInvitation,
    current_user: dict = Depends(get_current_active_user)
):
    """Invite user to team (owner or admin only)"""
    team = await check_team_permission(
        team_id, current_user["_id"], 
        [TeamRole.OWNER, TeamRole.ADMIN]
    )
    
    db = get_database()
    
    # Find user by email
    invited_user = await db.users.find_one({"email": invitation.email})
    if not invited_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is already a member
    for member in team.get("members", []):
        if str(member["user_id"]) == str(invited_user["_id"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this team"
            )
    
    # Add user to team
    new_member = TeamMember(
        user_id=str(invited_user["_id"]),
        role=invitation.role,
        joined_at=datetime.utcnow()
    )
    
    await db.teams.update_one(
        {"_id": ObjectId(team_id)},
        {
            "$push": {"members": new_member.dict()},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return {"message": f"User {invitation.email} invited to team successfully"}

@router.delete("/{team_id}/members/{user_id}")
async def remove_team_member(
    team_id: str,
    user_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Remove member from team (owner or admin only, or self)"""
    team = await check_team_permission(team_id, current_user["_id"])
    
    # Check permissions
    if (str(current_user["_id"]) != user_id and 
        str(team["owner_id"]) != str(current_user["_id"])):
        # Check if current user is admin
        current_user_role = None
        for member in team.get("members", []):
            if str(member["user_id"]) == str(current_user["_id"]):
                current_user_role = member["role"]
                break
        
        if current_user_role != TeamRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to remove team member"
            )
    
    db = get_database()
    
    # Remove user from team
    await db.teams.update_one(
        {"_id": ObjectId(team_id)},
        {
            "$pull": {"members": {"user_id": user_id}},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return {"message": "Member removed from team successfully"}

@router.put("/{team_id}/members/{user_id}/role")
async def update_member_role(
    team_id: str,
    user_id: str,
    role: TeamRole,
    current_user: dict = Depends(get_current_active_user)
):
    """Update member role (owner or admin only)"""
    team = await check_team_permission(
        team_id, current_user["_id"], 
        [TeamRole.OWNER, TeamRole.ADMIN]
    )
    
    db = get_database()
    
    # Update member role
    await db.teams.update_one(
        {"_id": ObjectId(team_id), "members.user_id": user_id},
        {
            "$set": {
                "members.$.role": role,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Member role updated successfully"}
