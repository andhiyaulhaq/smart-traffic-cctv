from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Traffic CCTV"
    HLS_STREAM_URL: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
