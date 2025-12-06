from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import uuid4


class UserSession(BaseModel):
    """Model for user session data"""
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    device_info: Optional[dict] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChatMessage(BaseModel):
    """Model for chat message data"""
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    role: str  # "user", "model", or "system"
    message_text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tokens_used: Optional[int] = None
    model_version: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SessionMetadata(BaseModel):
    """Model for session metadata"""
    session_id: str
    last_active: datetime = Field(default_factory=datetime.utcnow)
    extension_version: Optional[str] = None
    cluster_used: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Request/Response models for API endpoints
class CreateSessionRequest(BaseModel):
    """Request model for creating a new session"""
    user_id: Optional[str] = None
    device_info: Optional[dict] = None


class CreateSessionResponse(BaseModel):
    """Response model for session creation"""
    session_id: str
    created_at: datetime


class SaveMessageRequest(BaseModel):
    """Request model for saving a message"""
    session_id: str
    role: str
    message_text: str
    tokens_used: Optional[int] = None
    model_version: Optional[str] = None


class GetMessagesResponse(BaseModel):
    """Response model for retrieving messages"""
    session_id: str
    messages: list[ChatMessage]
    total_count: int
