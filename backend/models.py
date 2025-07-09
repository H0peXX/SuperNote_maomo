from sqlmodel import SQLModel, Field
from typing import Optional
import uuid
from datetime import datetime

# 1. USERS
class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str
    email: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# 2. TEAMS
class Team(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    description: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

# 3. TEAM MEMBERS
class TeamMember(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID
    team_id: uuid.UUID
    role: Optional[str]
    joined_at: datetime = Field(default_factory=datetime.utcnow)

# 4. PDF FILES
class PDFFile(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID
    team_id: Optional[uuid.UUID] = None
    file_name: str
    original_text: Optional[str] = None
    formatted_text: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# 5. TEAM SUMMARY
class TeamSummary(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    team_id: uuid.UUID
    aggregated_summary: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# 6. TEAM SUMMARY - PDF FILE RELATIONSHIP
class TeamSummaryPDF(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    team_summary_id: uuid.UUID
    pdf_file_id: uuid.UUID
