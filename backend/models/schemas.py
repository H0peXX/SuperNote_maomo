from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"

class TeamRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

class NoteStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class FactCheckStatus(str, Enum):
    VERIFIED = "verified"
    QUESTIONABLE = "questionable"
    INACCURATE = "inaccurate"
    PENDING = "pending"

# User Models
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)

class UserResponse(UserBase):
    id: str = Field(..., alias="_id")
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Team Models
class TeamMember(BaseModel):
    user_id: str
    role: TeamRole
    joined_at: datetime

class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class TeamResponse(TeamBase):
    id: str = Field(..., alias="_id")
    owner_id: str
    members: List[TeamMember] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

class TeamInvitation(BaseModel):
    email: EmailStr
    role: TeamRole = TeamRole.MEMBER

# Topic Models
class TopicBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    tags: List[str] = []

class TopicCreate(TopicBase):
    team_id: str

class TopicUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None

class TopicResponse(TopicBase):
    id: str = Field(..., alias="_id")
    team_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

# Note Models
class FactCheck(BaseModel):
    claim: str
    status: FactCheckStatus
    explanation: str
    sources: List[str] = []
    confidence: float = Field(..., ge=0, le=1)

class Comment(BaseModel):
    id: str
    user_id: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class NoteVersion(BaseModel):
    version: int
    content: str
    created_by: str
    created_at: datetime
    changes_summary: Optional[str] = None

class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str
    topic_id: str
    status: NoteStatus = NoteStatus.DRAFT

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    status: Optional[NoteStatus] = None

class NoteResponse(NoteBase):
    id: str = Field(..., alias="_id")
    team_id: str
    created_by: str
    collaborators: List[str] = []
    fact_checks: List[FactCheck] = []
    comments: List[Comment] = []
    versions: List[NoteVersion] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

# AI Service Models
class AIProcessRequest(BaseModel):
    text: str
    language: str = "English"
    operation: str  # "format", "summarize", "fact_check", "quiz"

class AIProcessResponse(BaseModel):
    result: str
    confidence: Optional[float] = None
    additional_data: Optional[Dict[str, Any]] = None

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: Optional[str] = None

class QuizResponse(BaseModel):
    questions: List[QuizQuestion]
    total_questions: int

# WebSocket Models
class WebSocketMessage(BaseModel):
    type: str  # "note_update", "user_join", "user_leave", "cursor_update"
    data: Dict[str, Any]
    timestamp: datetime
    user_id: str

# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
