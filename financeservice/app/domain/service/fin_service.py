import os
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from app.domain.service.company_info_service import CompanyInfoService
from app.domain.service.financial_statement_service import FinancialStatementService
from app.domain.service.ratio_service import RatioService
from app.domain.model.schema.schema import (
    FinancialMetricsResponse,
    FinancialMetrics,
    GrowthData,
    DebtLiquidityData
)
from app.domain.model.schema.company_schema import CompanySchema
from app.domain.model.schema.financial_schema import FinancialSchema
from app.domain.model.schema.metric_schema import MetricSchema
from app.domain.model.schema.report_schema import ReportSchema
from app.domain.model.schema.statement_schema import StatementSchema

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
    재무 정보 서비스 파사드 클래스.
    
    다른 서비스들의 기능을 조합하여 제공합니다.
    - CompanyInfoService: 회사 정보 관련 기능
    - FinancialStatementService: 재무제표 관련 기능
    - RatioService: 재무비율 계산 기능
    """
    def __init__(self, db_session: AsyncSession):
        """서비스 초기화"""
        logger.info("FinService가 초기화되었습니다.")
        self.db_session = db_session
        self.company_info_service = CompanyInfoService(db_session)
        self.financial_statement_service = FinancialStatementService(db_session)
        self.ratio_service = RatioService(db_session)
        load_dotenv()
        self.api_key = os.getenv("DART_API_KEY")
        if not self.api_key:
            logger.error("DART API 키가 필요합니다.")
            raise ValueError("DART API 키가 필요합니다.")

    async def get_company_info(self, company_name: str) -> CompanySchema:
        """회사 정보를 조회합니다."""
        logger.info(f"회사 정보 조회 시작: {company_name}")
        return await self.company_info_service.get_company_info(company_name)

    async def get_financial_statements(self, company_name: str, year: Optional[int] = None) -> Dict[str, Any]:
        """재무제표 데이터를 조회하고 반환합니다.
        
        Args:
            company_name: 회사명
            year: 조회할 연도. None이면 최신 연도의 데이터를 조회
        
        Returns:
            재무제표 데이터
        """
        logger.info(f"재무제표 조회 시작 - 회사: {company_name}, 연도: {year}")
        try:
            return await self.financial_statement_service.get_formatted_financial_data(company_name, year)
        except Exception as e:
            logger.error(f"재무제표 조회 중 오류 발생: {str(e)}")
            raise

    async def fetch_and_save_financial_data(self, company_name: str, year: Optional[int] = None) -> Dict[str, Any]:
        """회사명으로 재무제표 데이터를 조회하고 저장합니다.
        
        Args:
            company_name: 회사명
            year: 조회할 연도. None이면 최신 연도의 데이터를 조회
        """
        logger.info(f"재무제표 데이터 조회 및 저장 시작 - 회사: {company_name}, 연도: {year}")
        return await self.financial_statement_service.fetch_and_save_financial_data(company_name, year)

    async def get_financial_metrics(self, company_name: str) -> FinancialMetricsResponse:
        """회사의 재무 지표를 계산하고 반환합니다."""
        logger.info(f"재무 지표 계산 시작 - 회사: {company_name}")
        try:
            # 회사 정보 먼저 조회
            company_info = await self.get_company_info(company_name)
            
            # 최근 3개년도 데이터를 모두 조회하기 위해 year=None으로 설정
            raw_data = await self.fetch_and_save_financial_data(company_name, None)
            
            if raw_data["status"] != "success" or not raw_data.get("data"):
                return self._empty_metrics_response(company_name)

            # RatioService를 사용하여 재무 지표 계산
            return await self.ratio_service.get_financial_metrics(
                company_info.corp_code,
                company_name,
                raw_data["data"]
            )

        except Exception as e:
            logger.error(f"재무 지표 계산 중 오류 발생: {str(e)}")
            raise

    async def get_financial_ratios(self, company_name: str, year: Optional[int] = None) -> Dict[str, Any]:
        """회사명으로 재무비율을 조회합니다.
        
        Args:
            company_name: 회사명
            year: 조회할 연도. None이면 직전 연도의 데이터를 조회
            
        Returns:
            재무비율 데이터
        """
        logger.info(f"재무비율 조회 시작 - 회사: {company_name}, 연도: {year}")
        try:
            # 회사 정보 조회
            company_info = await self.get_company_info(company_name)
            
            # 재무제표 데이터 조회 및 저장
            data = await self.fetch_and_save_financial_data(company_name, year)
            if data["status"] == "error" or not data.get("data"):
                return {
                    "status": "success",
                    "message": "재무비율이 성공적으로 조회되었습니다.",
                    "data": []
                }
            
            # 재무비율 계산 및 저장
            metrics = await self.get_financial_metrics(company_name)
            
            # 연도별 데이터 추출 및 포맷팅
            ratios_data = self._format_ratios_data(metrics)
            
            return {
                "status": "success",
                "message": "재무비율이 성공적으로 조회되었습니다.",
                "data": ratios_data
            }
            
        except ValueError as e:
            error_message = str(e)
            logger.error(f"회사명 관련 오류: {error_message}")
            raise
        except Exception as e:
            error_message = str(e)
            logger.error(f"기타 오류: {error_message}")
            raise

    def _format_ratios_data(self, metrics) -> List[Dict[str, Any]]:
        """재무비율 데이터를 포맷팅합니다."""
        ratios_data = []
        if metrics and metrics.financialMetrics and metrics.financialMetrics.years:
            for i, year in enumerate(metrics.financialMetrics.years):
                ratio = {
                    "사업연도": year,
                    "부채비율": metrics.debtLiquidityData.debtRatio[i] if i < len(metrics.debtLiquidityData.debtRatio) else None,
                    "유동비율": metrics.debtLiquidityData.currentRatio[i] if i < len(metrics.debtLiquidityData.currentRatio) else None,
                    "영업이익률": metrics.financialMetrics.operatingMargin[i] if i < len(metrics.financialMetrics.operatingMargin) else None,
                    "순이익률": metrics.financialMetrics.netMargin[i] if i < len(metrics.financialMetrics.netMargin) else None,
                    "ROE": metrics.financialMetrics.roe[i] if i < len(metrics.financialMetrics.roe) else None,
                    "ROA": metrics.financialMetrics.roa[i] if i < len(metrics.financialMetrics.roa) else None
                }
                
                # 성장률은 마지막 연도 제외
                if i < len(metrics.growthData.years):
                    ratio.update({
                        "매출액증가율": metrics.growthData.revenueGrowth[i] if i < len(metrics.growthData.revenueGrowth) else None,
                        "순이익증가율": metrics.growthData.netIncomeGrowth[i] if i < len(metrics.growthData.netIncomeGrowth) else None
                    })
                
                ratios_data.append(ratio)
        
        return ratios_data

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