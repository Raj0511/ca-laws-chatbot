from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.knowledge import DocumentItem, EmbeddingChunk
# Import your models here later so Beanie knows about them
from app.models.user import User
from app.models.chat import Chat, Message


async def init_db():
    # 1. Create the Motor Client (Async)
    client = AsyncIOMotorClient(settings.MONGO_URI)
    
    # 2. Select the Database
    database = client[settings.DB_NAME]
    
    # 3. Initialize Beanie
    # document_models will handle the mapping between Python classes and Mongo collections
    await init_beanie(
        database=database,
        document_models=[
            User,
            Chat,
            Message,
            DocumentItem,
            EmbeddingChunk
        ]
    )
    
    print(f"✅ Connected to MongoDB: {settings.DB_NAME}")