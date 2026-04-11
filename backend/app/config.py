from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Traffic CCTV"
    HLS_STREAM_URL: str = ""
    
    # Performance Settings
    FRAME_SKIP: int = 2  # Process every Nth frame
    MODEL_WARMUP: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
