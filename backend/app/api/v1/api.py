from fastapi import APIRouter
from app.api.v1.endpoints import auth, chat, websockets, knowledge

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# --- THIS LINE IS CRITICAL ---
api_router.include_router(chat.router, prefix="/chats", tags=["Chat"]) 
# -----------------------------
api_router.include_router(websockets.router, prefix="/ws", tags=["WebSockets"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge"])
