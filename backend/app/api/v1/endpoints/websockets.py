from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from typing import Optional
from beanie import PydanticObjectId

from app.api import deps
from app.models.user import User
from app.models.chat import Chat, Message, RoleEnum
from app.services.llm_service import generate_response
from app.core.config import settings
from jose import jwt, JWTError

router = APIRouter()

# --- AUTHENTICATION HELPER ---
# WebSockets cannot easily send headers from the browser. 
# We usually pass the token in the URL: ws://localhost:8000/ws/{chat_id}?token=xyz
async def get_user_from_token(token: str) -> Optional[User]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = payload.get("sub")
        if token_data is None:
            return None
        return await User.get(token_data)
    except JWTError:
        return None

# --- WEBSOCKET ENDPOINT ---
@router.websocket("/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    chat_id: PydanticObjectId,
    token: str = Query(...) # Require token in URL
):
    # 1. AUTHENTICATION (Before Accepting)
    user = await get_user_from_token(token)
    if not user:
        # Close with Policy Violation code if auth fails
        await websocket.close(code=1008) 
        return

    # 2. VALIDATION (Does chat exist? Is it yours?)
    chat = await Chat.get(chat_id)
    if not chat or chat.user_id != user.id:
        await websocket.close(code=1008)
        return

    # 3. ACCEPT CONNECTION
    await websocket.accept()
    
    try:
        while True:
            # 4. RECEIVE USER MESSAGE
            data = await websocket.receive_text()
            
            # 5. SAVE USER MESSAGE TO DB
            user_msg = Message(
                chat_id=chat.id,
                role=RoleEnum.user,
                content=data
            )
            await user_msg.insert()
            

            history = await Message.find(Message.chat_id == chat.id)\
                .sort(+Message.timestamp)\
                .limit(10)\
                .to_list()

            # 6. TRIGGER AI (The "Brain")
            # In the future, we will fetch history here to pass context

            previous_history = [m for m in history if m.id != user_msg.id]

            ai_text = await generate_response(data, previous_history)
            
            # 7. SAVE AI MESSAGE TO DB
            ai_msg = Message(
                chat_id=chat.id,
                role=RoleEnum.assistant,
                content=ai_text
            )
            await ai_msg.insert()
            
            # 8. UPDATE CHAT "UPDATED_AT"
            chat.title = data[:30] + "..." if chat.title == "New Chat" else chat.title
            await chat.save()

            # 9. SEND RESPONSE TO FRONTEND
            # We send a JSON structure so the frontend knows who sent it
            await websocket.send_json({
                "role": "assistant",
                "content": ai_text,
                "timestamp": ai_msg.timestamp.isoformat()
            })
            
    except WebSocketDisconnect:
        print(f"User {user.email} disconnected from chat {chat_id}")