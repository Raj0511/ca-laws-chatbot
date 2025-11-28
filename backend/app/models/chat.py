from beanie import Document, PydanticObjectId
from pydantic import Field
from datetime import datetime
from typing import Optional
from enum import Enum

class RoleEnum(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"

# 1. The Conversation Container (Lightweight)
class Chat(Document):
    user_id: PydanticObjectId # Link to the User who owns this chat
    title: str = "New Chat"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "chats"
        
    async def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        await super().save(*args, **kwargs)

# 2. The Individual Messages (Heavy)
class Message(Document):
    chat_id: PydanticObjectId # Link to the Chat above
    role: RoleEnum            # Who said it?
    content: str              # The text (or JSON for complex tool use)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "messages"
        # We index chat_id because we will frequently ask:
        # "Give me all messages for Chat X sorted by time"
        indexes = [
            "chat_id"
        ]