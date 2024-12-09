import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
  GROQ_API_KEY = os.getenv('GROQ_API_KEY')
  SERVICES_PATH = os.getenv('SERVICES_PATH')
  MEMBERS_PATH = os.getenv('MEMBERS_PATH')
  ENROLLMENT_PATH = os.getenv('ENROLLMENT_PATH')
  PROVIDERS_PATH = os.getenv('PROVIDERS_PATH')

settings = Settings()