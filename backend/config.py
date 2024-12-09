# config.py
from pydantic_settings import BaseSettings
from typing import Dict

class Settings(BaseSettings):
    # AWS Settings
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-2"
    S3_BUCKET: str = "lohaki-data"
    
    SERVICES_PATH: str = "Claims_Services"
    MEMBERS_PATH: str = "Claims_Member"
    ENROLLMENT_PATH: str = "Claims_Enrollment"
    PROVIDERS_PATH: str = "Claims_Provider"
    
    # LLM Settings
    GROQ_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()