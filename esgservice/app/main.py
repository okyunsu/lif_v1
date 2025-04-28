from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import logging
from app.api.esg_router import router as esg_api_router

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("esg_api")

# .env 파일 로드
load_dotenv()
    
# ✅ 애플리케이션 시작 시 실행
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 ESG API 서비스 시작")
    yield
    logger.info("🛑 ESG API 서비스 종료")


# ✅ FastAPI 앱 생성 
app = FastAPI(
    title="ESG API",
    description="ESG API Service",
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

# ✅ 서브 라우터 생성
esg_router = APIRouter(prefix="/esg", tags=["ESG API"])

# ✅ 서브 라우터와 엔드포인트를 연결함
app.include_router(esg_api_router, prefix="/esg", tags=["ESG API"])

# ✅ 서브 라우터 등록
app.include_router(esg_router, tags=["ESG API"])

