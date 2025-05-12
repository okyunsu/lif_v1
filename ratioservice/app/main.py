from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import logging
from app.api.ratio_router import router as ratio_router

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("finance_api")

# .env 파일 로드
load_dotenv()
    
# ✅ 애플리케이션 시작 시 실행
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Finance API 서비스 시작")
    yield
    logger.info("🛑 Finance API 서비스 종료")


# ✅ FastAPI 앱 생성 
app = FastAPI(
    title="Finance API",
    description="Finance API Service",
    version="0.1.0",
)

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 서브 라우터 등록 (prefix 한 번만 설정)
app.include_router(ratio_router, prefix="/ratio", tags=["Ratio API"])

