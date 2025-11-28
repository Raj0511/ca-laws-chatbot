from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.client import init_db
from app.core.config import settings
from app.api.v1.api import api_router
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP LOGIC ---
    print("🚀 Starting application...")
    await init_db()
    
    yield # The application runs here
    
    # --- SHUTDOWN LOGIC ---
    print("🛑 Shutting down...")
    # Close connections if necessary (Motor handles this well automatically, but good to know)

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with ["http://localhost:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def health_check():
    return {"status": "ok", "db": "connected"}