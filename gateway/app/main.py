import json
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
import sys
from dotenv import load_dotenv
from app.domain.model.service_proxy_factory import ServiceProxyFactory
from contextlib import asynccontextmanager
from app.domain.model.request_model import FinanceRequest
from app.domain.model.service_type import ServiceType

# ✅로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("gateway_api")

# ✅ .env 파일 로드
load_dotenv()

# ✅ 애플리케이션 시작 시 실행
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 서비스 시작")
    yield
    logger.info("🛑 Gateway API 서비스 종료")


# ✅ FastAPI 앱 생성 
app = FastAPI(
    title="Gateway API",
    description="Gateway API for jinmini.com",
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

# ✅ 메인 라우터 생성
gateway_router = APIRouter(prefix="/e/v3", tags=["Gateway API"])

# ✅ 헬스 체크 엔드포인트 추가
@gateway_router.get("/health", summary="테스트 엔드포인트")
async def health_check():
    return {"status": "healthy!"}

# ✅ 메인 라우터 실행

# GET
@gateway_router.get("/{service}/{path:path}", summary="GET 프록시")
async def proxy_get(
    service: ServiceType, 
    path: str, 
    request: Request
):
    factory = ServiceProxyFactory(service_type=service)
    response = await factory.request(
        method="GET",
        path=path,
        headers=request.headers.raw
    )
    return JSONResponse(content=response.json(), status_code=response.status_code)

# POST

@gateway_router.post("/{service}/{path:path}", summary="POST 프록시")
async def proxy_post(
    service: ServiceType, 
    path: str, 
    request_body: FinanceRequest,
    request: Request
):
    print(f"🌈Received request for service: {service}, path: {path}")
    factory = ServiceProxyFactory(service_type=service)
    body = request_body.model_dump_json()
    print(f"Request body: {body}")
    response = await factory.request(
        method="POST",
        path=path,
        headers=request.headers.raw,
        body=body
    )
    if response.status_code == 200:
        try:
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
        except json.JSONDecodeError:
            # 응답이 JSON이 아닌 경우
            return JSONResponse(
                content={"detail": "⚠️Invalid JSON response from service"},
                status_code=500
            )
    else:
        # 에러 응답 처리
        return JSONResponse(
            content={"detail": f"Service error: {response.text}"},
            status_code=response.status_code
        )

# PUT
@gateway_router.put("/{service}/{path:path}", summary="PUT 프록시")
async def proxy_put(service: ServiceType, path: str, request: Request):
    factory = ServiceProxyFactory(service_type=service)
    response = await factory.request(
        method="PUT",
        path=path,
        headers=request.headers.raw,
        body=await request.body()
    )
    return JSONResponse(content=response.json(), status_code=response.status_code)

# DELETE
@gateway_router.delete("/{service}/{path:path}", summary="DELETE 프록시")
async def proxy_delete(service: ServiceType, path: str, request: Request):
    factory = ServiceProxyFactory(service_type=service)
    response = await factory.request(
        method="DELETE",
        path=path,
        headers=request.headers.raw,
        body=await request.body()
    )
    return JSONResponse(content=response.json(), status_code=response.status_code)

# PATCH
@gateway_router.patch("/{service}/{path:path}", summary="PATCH 프록시")
async def proxy_patch(service: ServiceType, path: str, request: Request):
    factory = ServiceProxyFactory(service_type=service)
    response = await factory.request(
        method="PATCH",
        path=path,
        headers=request.headers.raw,
        body=await request.body()
    )
    return JSONResponse(content=response.json(), status_code=response.status_code)

# ✅ 라우터 등록
app.include_router(gateway_router)

# ✅ 서버 실행
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True) 

