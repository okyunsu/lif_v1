import os
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from app.domain.service.company_info_service import CompanyInfoService
from app.domain.service.financial_statement_service import FinancialStatementService
from app.domain.model.schema.company_schema import CompanySchema
from app.domain.model.schema.financial_schema import FinancialSchema

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
    """
    def __init__(self, db_session: AsyncSession):
        """서비스 초기화"""
        logger.info("FinService가 초기화되었습니다.")
        self.db_session = db_session
        self.company_info_service = CompanyInfoService(db_session)
        self.financial_statement_service = FinancialStatementService(db_session)
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

    async def crawl_and_save_financial_data(self, company_name: str, year: Optional[int] = None) -> bool:
        """회사명으로 재무제표 데이터를 크롤링하고 저장합니다.
        
        Args:
            company_name: 회사명
            year: 조회할 연도. None이면 최신 연도의 데이터를 조회
            
        Returns:
            bool: 크롤링 및 저장 성공 여부
        """
        logger.info(f"재무제표 데이터 크롤링 및 저장 시작 - 회사: {company_name}, 연도: {year}")
        try:
            result = await self.financial_statement_service.fetch_and_save_financial_data(company_name, year)
            return result["status"] == "success"
        except Exception as e:
            logger.error(f"재무제표 데이터 크롤링 및 저장 중 오류 발생: {str(e)}")
            return False