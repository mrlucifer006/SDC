from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True, index=True)
    is_admin: bool = Field(default=False)
    is_locked: bool = Field(default=False)
    total_score: int = Field(default=0)

class User(UserBase, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

    progress: List["UserProgress"] = Relationship(back_populates="user")
    submissions: List["Submission"] = Relationship(back_populates="user")

class Gate(SQLModel, table=True):
    __tablename__ = "gates"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    cipher_type: str
    points_awarded: int
    prerequisite_gate_id: Optional[int] = Field(default=None, foreign_key="gates.id")
    
    # Competitive Programming Fields
    problem_statement: str
    sample_input: str
    sample_output: str
    hidden_input: str
    hidden_output: str

class UserProgress(SQLModel, table=True):
    __tablename__ = "user_progress"
    user_id: int = Field(foreign_key="users.id", primary_key=True)
    gate_id: int = Field(foreign_key="gates.id", primary_key=True)
    is_unlocked: bool = Field(default=False)
    is_completed: bool = Field(default=False)
    score: int = Field(default=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    user: User = Relationship(back_populates="progress")

class Submission(SQLModel, table=True):
    __tablename__ = "game_submissions"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    gate_id: int = Field(foreign_key="gates.id")
    passed: bool
    execution_time_ms: float
    code_snippet: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(back_populates="submissions")

# Pydantic Schemas for API
class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

class Token(SQLModel):
    access_token: str
    token_type: str
