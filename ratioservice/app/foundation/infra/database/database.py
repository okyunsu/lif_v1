from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# 환경 변수 로드
env = os.getenv("APP_ENV", "development")
if env == "development":
    load_dotenv(".env")
else:
    # 프로덕션 환경에서는 Railway의 환경 변수를 사용
    load_dotenv()

# 데이터베이스 URL 설정
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# 호스트 이름을 fin_db로 수정
if "db:5432" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("db:5432", "fin_db:5432")

logger.info(f"Connecting to database with URL: {DATABASE_URL}")

# 비동기 엔진 생성
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # 연결 상태 확인
    pool_size=5,  # 연결 풀 크기
    max_overflow=10  # 최대 추가 연결 수
)

# 비동기 세션 팩토리 생성
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base 클래스 생성
Base = declarative_base()

async def get_db_session() -> AsyncSession:
    """데이터베이스 세션을 반환합니다."""
    session = async_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

async def init_db():
    """데이터베이스 초기화 함수"""
    try:
        async with engine.begin() as conn:
            if env == "development":
                # 개발 환경에서만 테이블 재생성
                logger.info("Dropping existing tables...")
                await conn.run_sync(Base.metadata.drop_all)
                logger.info("Creating new tables...")
                await conn.run_sync(Base.metadata.create_all)
            else:
                # 프로덕션 환경에서는 테이블 생성만
                logger.info("Creating tables if they don't exist...")
                await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise 