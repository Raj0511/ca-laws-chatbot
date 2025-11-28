from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from beanie import PydanticObjectId
from app.api import deps
from app.models.user import User
from app.models.chat import Chat, Message
from app.schemas.chat import ChatCreate, ChatResponse, MessageResponse

router = APIRouter()

# 1. GET ALL CHATS (For the Sidebar)
@router.get("/", response_model=List[ChatResponse])
async def get_chats(
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 50
):
    """
    Retrieve all chats for the current user.
    Sorted by most recently updated.
    """
    chats = await Chat.find(Chat.user_id == current_user.id)\
        .sort(-Chat.updated_at)\
        .skip(skip)\
        .limit(limit)\
        .to_list()
    return chats

# 2. CREATE NEW CHAT (For the "New Chat" button)
@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_in: ChatCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Create a new chat container.
    """
    chat = Chat(
        user_id=current_user.id,
        title=chat_in.title
    )
    await chat.insert()
    return chat

# 3. GET CHAT DETAILS (Check Ownership)
@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: PydanticObjectId,
    current_user: User = Depends(deps.get_current_user)
):
    chat = await Chat.get(chat_id)
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # CRITICAL SECURITY CHECK
    if chat.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this chat")
        
    return chat

# 4. GET MESSAGES (For the Main Window)
@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_history(
    chat_id: PydanticObjectId,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get all messages for a specific chat.
    """
    # 1. Verify Chat Existence & Ownership first
    chat = await Chat.get(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # 2. Fetch Messages
    # Sort by timestamp ascending (oldest -> newest) so conversation flows correctly
    messages = await Message.find(Message.chat_id == chat.id)\
        .sort(+Message.timestamp)\
        .to_list()
        
    return messages

# 5. DELETE CHAT
@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: PydanticObjectId,
    current_user: User = Depends(deps.get_current_user)
):
    chat = await Chat.get(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Delete the chat container
    await chat.delete()
    
    # Cleanup: Delete all messages associated with this chat
    await Message.find(Message.chat_id == chat.id).delete()
    
    return None