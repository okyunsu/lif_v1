from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import logging
from app.api.stock_router import router as stock_api_router

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("stock_api")

# .env 파일 로드
load_dotenv()
    
# ✅ 애플리케이션 시작 시 실행
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Stock API 서비스 시작")
    yield
    logger.info("🛑 Stock API 서비스 종료")


# ✅ FastAPI 앱 생성 
app = FastAPI(
    title="Stock API",
    description="Stock API Service",
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
stock_router = APIRouter(prefix="/stock", tags=["Stock API"])

# ✅ 서브 라우터와 엔드포인트를 연결함
app.include_router(stock_api_router, prefix="/stock", tags=["Stock API"])

# ✅ 서브 라우터 등록
app.include_router(stock_router, tags=["Stock API"])

