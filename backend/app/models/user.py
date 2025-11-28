from beanie import Document, Indexed
from pydantic import Field, EmailStr
from datetime import datetime
from typing import Optional
import uuid

class User(Document):
    # 'id' is automatically handled by Beanie (MongoDB _id)

    # 1. Identity
    # Indexed(str, unique=True) creates a unique index in Mongo
    # This prevents two users from registering with the same email.
    email: Indexed(str, unique=True) 
    
    # 2. Security
    # NEVER store plain text. This will hold the Bcrypt hash.
    hashed_password: str 
    
    # 3. Profile
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    
    # 4. Timestamps
    # default_factory ensures the time is calculated when the object is created
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        # The name of the collection in MongoDB
        name = "users"

    # Optional: Helper method to update timestamp on save
    async def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        await super().save(*args, **kwargs)