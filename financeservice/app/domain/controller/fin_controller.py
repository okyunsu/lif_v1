from fastapi import HTTPException, Query
from app.domain.service.fin_service import FinService
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from typing import Optional
from app.domain.model.schema.schema import (
    FinancialMetricsResponse,
    FinancialMetrics,
    GrowthData,
    DebtLiquidityData
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FinController:
    def __init__(self, db_session: AsyncSession):
        logger.info("FinController가 초기화되었습니다.")
        self.db_session = db_session
        self.service = FinService(db_session)

    async def get_financial(
        self, 
        company_name: str = Query(..., description="회사명"),
        year: Optional[int] = Query(None, description="조회할 연도. 지정하지 않으면 직전 연도의 데이터를 조회")
    ) -> FinancialMetricsResponse:
        """회사명으로 재무제표를 조회합니다.
        
        Args:
            company_name: 회사명
            year: 조회할 연도. None이면 직전 연도의 데이터를 조회
        """
        logger.info(f"재무제표 조회 요청 - 회사: {company_name}, 연도: {year}")
        try:
            # year 파라미터 정제
            actual_year = None
            if year and isinstance(year, int):
                actual_year = year
            
            # 재무 지표 조회 - 직접 metrics 조회
            return await self.service.get_financial_metrics(company_name)
            
        except ValueError as e:
            error_message = str(e)
            logger.error(f"회사명 관련 오류: {error_message}")
            raise HTTPException(status_code=400, detail=error_message)
        except Exception as e:
            error_message = str(e)
            logger.error(f"기타 오류: {error_message}")
            raise HTTPException(status_code=500, detail=error_message)

    async def get_financial_ratios(
        self, 
        company_name: str = Query(..., description="회사명"),
        year: Optional[int] = Query(None, description="조회할 연도. 지정하지 않으면 직전 연도의 데이터를 조회")
    ):
        """회사명으로 재무비율을 조회합니다.
        
        Args:
            company_name: 회사명
            year: 조회할 연도. None이면 직전 연도의 데이터를 조회
        """
        logger.info(f"재무비율 조회 요청 - 회사: {company_name}, 연도: {year}")
        try:
            return await self.service.get_financial_ratios(company_name, year)
        except ValueError as e:
            error_message = str(e)
            logger.error(f"회사명 관련 오류: {error_message}")
            raise HTTPException(status_code=400, detail=error_message)
        except Exception as e:
            error_message = str(e)
            logger.error(f"기타 오류: {error_message}")
            raise HTTPException(status_code=500, detail=error_message)