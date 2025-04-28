from fastapi import APIRouter, Request
import logging
from app.domain.controller.fin_controller import FinController
from app.foundation.infra.database.database import get_db_session
from app.domain.model.schema.schema import (
    CompanyNameRequest,
    FinancialMetricsResponse,
)
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# 로거 설정
logger = logging.getLogger("fin_router")
logger.setLevel(logging.INFO)
router = APIRouter()

# GET
@router.get("/financial", summary="모든 회사 목록 조회")
async def get_all_companies():
    """
    등록된 모든 회사의 목록을 조회합니다.
    """
    print("📋 모든 회사 목록 조회")
    logger.info("📋 모든 회사 목록 조회")
    
    # 샘플 데이터
    companies = [
        {"id": 1, "name": "샘플전자", "industry": "전자제품"},
        {"id": 2, "name": "테스트기업", "industry": "소프트웨어"},
        {"id": 3, "name": "예시주식", "industry": "금융"}
    ]
    return {"companies": companies}

# POST
@router.post("/financial", summary="회사명으로 재무제표 조회 (최근 3개년)", response_model=FinancialMetricsResponse)
async def get_financial_by_name(
    payload: CompanyNameRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    회사명으로 재무제표를 조회합니다.
    - 최근 3개년(당기, 전기, 전전기)의 재무제표 데이터를 반환합니다.
    - 재무지표: 영업이익률, 순이익률, ROE, ROA
    - 성장성: 매출액 성장률, 순이익 성장률
    - 안정성: 부채비율, 유동비율
    """
    print(f"🕞🕞🕞🕞🕞🕞get_financial_by_name 호출 - 회사명: {payload.company_name}")
    logger.info(f"🕞🕞🕞🕞🕞🕞get_financial_by_name 호출 - 회사명: {payload.company_name}")
    controller = FinController(db)
    return await controller.get_financial(company_name=payload.company_name)
    # if payload.company_name == "샘플전자":
    #     return_model = {
    #         "companyName": payload.company_name,
    #         "financialMetrics": {
    #         "operatingMargin": [0.15, 0.14, 0.13],  # 최근 3년 데이터
    #         "netMargin": [0.12, 0.11, 0.10],
    #         "roe": [0.08, 0.07, 0.06],
    #         "roa": [0.05, 0.04, 0.03],
    #         "years": ["2023", "2022", "2021"]
    #         },
    #         "growthData": {
    #             "revenueGrowth": [0.20, 0.18, 0.15],
    #             "netIncomeGrowth": [0.10, 0.08, 0.05],
    #             "years": ["2023", "2022", "2021"]
    #         },
    #         "debtLiquidityData": {
    #             "debtRatio": [1.5, 1.6, 1.7],
    #             "currentRatio": [2.0, 1.9, 1.8],
    #             "years": ["2023", "2022", "2021"]
    #         }
    #     }
    # else:
    #     return_model = {
    #         "companyName": "존재하지 않는 회사",
    #         "financialMetrics": {
    #         "operatingMargin": [0.15, 0.14, 0.13],  # 최근 3년 데이터
    #         "netMargin": [0.12, 0.11, 0.10],
    #         "roe": [0.08, 0.07, 0.06],
    #         "roa": [0.05, 0.04, 0.03],
    #         "years": ["2023", "2022", "2021"]
    #         },
    #         "growthData": {
    #             "revenueGrowth": [0.20, 0.18, 0.15],
    #             "netIncomeGrowth": [0.10, 0.08, 0.05],
    #             "years": ["2023", "2022", "2021"]
    #         },
    #         "debtLiquidityData": {
    #             "debtRatio": [1.5, 1.6, 1.7],
    #             "currentRatio": [2.0, 1.9, 1.8],
    #             "years": ["2023", "2022", "2021"]
    #         }
    #     }
    # return return_model

# PUT
@router.put("/financial", summary="회사 정보 전체 수정")
async def update_company(request: Request):
    """
    회사 정보를 전체 수정합니다.
    """
    print("📝 회사 정보 전체 수정")
    logger.info("📝 회사 정보 전체 수정")
    
    # 샘플 응답
    return {
        "message": "회사 정보가 성공적으로 수정되었습니다.",
        "updated_data": {
            "name": "수정된샘플전자",
            "industry": "수정된산업"
        }
    }

# DELETE
@router.delete("/financial", summary="회사 정보 삭제")
async def delete_company():
    """
    회사 정보를 삭제합니다.
    """
    print("🗑️ 회사 정보 삭제")
    logger.info("🗑️ 회사 정보 삭제")
    
    # 샘플 응답
    return {
        "message": "회사 정보가 성공적으로 삭제되었습니다."
    }

# PATCH
@router.patch("/financial", summary="회사 정보 부분 수정")
async def patch_company(request: Request):
    """
    회사 정보를 부분적으로 수정합니다.
    """
    print("✏️ 회사 정보 부분 수정")
    logger.info("✏️ 회사 정보 부분 수정")
    
    # 샘플 응답
    return {
        "message": "회사 정보가 부분적으로 수정되었습니다.",
        "updated_fields": {
            "name": "부분수정샘플전자"
        }
    }
