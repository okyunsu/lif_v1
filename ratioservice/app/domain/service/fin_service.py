import logging
from typing import Dict, Any, Optional, List
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from app.domain.service.ratio_service import RatioService
from app.domain.model.schema.schema import (
    FinancialMetricsResponse,
    FinancialMetrics,
    GrowthData,
    DebtLiquidityData
)
from app.domain.model.schema.company_schema import CompanySchema

# 로깅 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 핸들러가 없으면 추가
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

class FinService:
    """
    파사드: DB에서 데이터 조회 + RatioService로 계산 위임
    컨트롤러에서 바로 사용 가능하도록 단순화
    """
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.ratio_service = RatioService(db_session)

    async def calculate_financial_ratios(self, company_name: str, year: Optional[int] = None) -> FinancialMetricsResponse:
        """
        회사명(및 연도)로 재무비율 계산
        """
        logger.info(f"재무비율 계산 요청 - 회사: {company_name}, 연도: {year}")
        try:
            return await self.ratio_service.calculate_financial_ratios(company_name, year)
        except Exception as e:
            logger.error(f"재무비율 계산 중 오류: {str(e)}")
            raise

    async def _get_company_info(self, company_name: str) -> Dict[str, str]:
        """DB에서 회사 정보를 조회합니다."""
        query = text("""
            SELECT corp_code, corp_name, stock_code 
            FROM companies 
            WHERE corp_name = :company_name 
            LIMIT 1
        """)
        result = await self.db_session.execute(query, {"company_name": company_name})
        row = result.fetchone()
        
        if row:
            return {
                "corp_code": row[0],
                "corp_name": row[1],
                "stock_code": row[2]
            }
        return None

    async def _get_financial_data(self, company_name: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """DB에서 재무제표 데이터를 조회합니다."""
        try:
            if year is not None:
                query = text("""
                    SELECT f.bsns_year, f.sj_div, s.sj_nm, f.account_nm, 
                           f.thstrm_amount, f.frmtrm_amount, f.bfefrmtrm_amount
                    FROM financials f
                    JOIN companies c ON f.corp_code = c.corp_code
                    JOIN statement s ON f.sj_div = s.sj_div
                    WHERE c.corp_name = :company_name
                    AND f.bsns_year = :year
                    ORDER BY f.bsns_year DESC, f.sj_div, f.ord
                """)
                result = await self.db_session.execute(query, {
                    "company_name": company_name,
                    "year": str(year)
                })
            else:
                # 최근 3개년도 데이터 조회
                query = text("""
                    SELECT f.bsns_year, f.sj_div, s.sj_nm, f.account_nm, 
                           f.thstrm_amount, f.frmtrm_amount, f.bfefrmtrm_amount
                    FROM financials f
                    JOIN companies c ON f.corp_code = c.corp_code
                    JOIN statement s ON f.sj_div = s.sj_div
                    WHERE c.corp_name = :company_name
                    AND f.bsns_year IN (
                        SELECT DISTINCT bsns_year 
                        FROM financials f2
                        JOIN companies c2 ON f2.corp_code = c2.corp_code
                        WHERE c2.corp_name = :company_name
                        ORDER BY bsns_year DESC
                        LIMIT 3
                    )
                    ORDER BY f.bsns_year DESC, f.sj_div, f.ord
                """)
                result = await self.db_session.execute(query, {
                    "company_name": company_name
                })
            
            # 결과를 딕셔너리로 변환
            data = []
            for row in result:
                row_dict = {}
                for idx, column in enumerate(result.keys()):
                    row_dict[column] = row[idx]
                data.append(row_dict)
            
            return data
        except Exception as e:
            logger.error(f"데이터 조회 중 오류 발생: {str(e)}")
            return []

    def _empty_metrics_response(self, company_name: str) -> FinancialMetricsResponse:
        """빈 재무 지표 응답을 생성합니다."""
        return FinancialMetricsResponse(
            companyName=company_name,
            financialMetrics=FinancialMetrics(
                operatingMargin=[], netMargin=[], roe=[], roa=[], years=[]
            ),
            growthData=GrowthData(
                revenueGrowth=[], netIncomeGrowth=[], years=[]
            ),
            debtLiquidityData=DebtLiquidityData(
                debtRatio=[], currentRatio=[], years=[]
            )
        )