from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId
from app.models.chat import RoleEnum

# --- MESSAGE SCHEMAS ---

class MessageCreate(BaseModel):
    # When user sends a message, we only need content
    content: str

class MessageResponse(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    role: RoleEnum
    content: str
    timestamp: datetime
    
    class Config:
        populate_by_name = True

# --- CHAT SCHEMAS ---

class ChatCreate(BaseModel):
    # Optional: User might start a chat with a specific title
    title: Optional[str] = "New Chat"

class ChatResponse(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    title: str
    updated_at: datetime
    # We do NOT include the full list of messages here. 
    # That is fetched via a separate API call for performance.

    class Config:
        populate_by_name = True