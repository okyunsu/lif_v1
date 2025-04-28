import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # 데이터베이스 설정
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/findb")
    
    # DART API 설정
    DART_API_KEY: str = os.getenv("DART_API_KEY", "")
    DART_API_URL: str = "https://opendart.fss.or.kr/api"

settings = Settings() 