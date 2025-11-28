from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from beanie import PydanticObjectId

# 1. Shared Properties
# These fields are common to reading, creating, and updating
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True

# 2. Input Schema (Client -> Server)
# We ONLY ask for the password when creating a user (or resetting).
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Must be at least 8 chars")

# 3. Output Schema (Server -> Client)
# Notice: 'password' is GONE. We never send it back.
class UserResponse(UserBase):
    id: PydanticObjectId = Field(alias="_id") # Maps MongoDB _id to JSON 'id'
    
    class Config:
        # This allows Pydantic to read data from the Beanie DB object
        from_attributes = True
        # This ensures the _id is serialized correctly to a string
        populate_by_name = True

# 4. Token Schema
# What the /login endpoint returns
class Token(BaseModel):
    access_token: str
    token_type: str