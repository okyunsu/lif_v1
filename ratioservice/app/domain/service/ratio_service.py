from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from sqlalchemy import text

from app.domain.model.schema.schema import FinancialMetricsResponse
from .financial_data_processor import FinancialDataProcessor
from .ratio_calculator import RatioCalculator
from .growth_rate_calculator import GrowthRateCalculator
from .response_builder import ResponseBuilder

logger = logging.getLogger(__name__)

class RatioService:
    """재무비율 계산 서비스"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.data_processor = FinancialDataProcessor()
        self.ratio_calculator = RatioCalculator()
        self.growth_calculator = GrowthRateCalculator()
        self.response_builder = ResponseBuilder()

    async def calculate_financial_ratios(self, company_name: str, year: Optional[int] = None) -> FinancialMetricsResponse:
        """financials 테이블에서 데이터 조회 후 재무비율 계산"""
        try:
            # 1. financials 테이블에서 데이터 조회
            query = text("""
                SELECT f.bsns_year, f.account_nm, f.thstrm_amount, f.frmtrm_amount, f.bfefrmtrm_amount
                FROM financials f
                JOIN companies c ON f.corp_code = c.corp_code
                WHERE c.corp_name = :company_name
                AND f.bsns_year IN (
                    SELECT DISTINCT bsns_year
                    FROM financials f2
                    JOIN companies c2 ON f2.corp_code = c2.corp_code
                    WHERE c2.corp_name = :company_name
                    ORDER BY bsns_year DESC
                    LIMIT 3
                )
                ORDER BY f.bsns_year DESC, f.ord
            """)
            result = await self.db_session.execute(query, {"company_name": company_name})
            rows = result.mappings().all()  # 딕셔너리 리스트

            if not rows:
                logger.error(f"재무제표 데이터가 없습니다: {company_name}")
                raise ValueError(f"재무제표 데이터가 없습니다: {company_name}")

            # 2. 데이터 전처리 (연도별, 계정명별로 정리)
            years_data = {}
            for row in rows:
                year = row["bsns_year"]
                if year not in years_data:
                    years_data[year] = {}
                account = row["account_nm"]
                years_data[year][account] = {
                    "thstrm": float(row["thstrm_amount"] or 0),
                    "frmtrm": float(row["frmtrm_amount"] or 0),
                    "bfefrmtrm": float(row["bfefrmtrm_amount"] or 0)
                }

            # 3. 대상 연도 결정
            target_years = self.data_processor.get_target_years(years_data)

            # 4. 재무비율 계산
            ratios = self.ratio_calculator.calculate_all_ratios(years_data, target_years)

            # 5. 성장률 계산
            growth_rates = self.growth_calculator.calculate_growth_rates(years_data, target_years)

            # 6. 응답 생성
            return self.response_builder.build_metrics_response(
                company_name=company_name,
                target_years=target_years,
                ratios=ratios,
                growth_rates=growth_rates
            )
        except Exception as e:
            logger.error(f"재무비율 계산 중 오류 발생: {str(e)}")
            raise 