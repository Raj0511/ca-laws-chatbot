from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Config
    PROJECT_NAME: str = "AI Chatbot"
    API_V1_STR: str = "/api/v1"
    
    # Database Config
    MONGO_URI: str
    DB_NAME: str = "chatbot_db"

    # Security (We will need these later)
    SECRET_KEY: str = "CHANGE_THIS_IN_PROD_TO_A_LONG_RANDOM_STRING"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


    GROQ_API_KEY: str
    GOOGLE_API_KEY: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()