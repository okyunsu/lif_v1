from typing import Dict, Any, List, Optional
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.model.schema.company_schema import CompanySchema
from app.domain.model.schema.financial_schema import FinancialSchema
from app.domain.model.schema.report_schema import ReportSchema
from app.domain.model.schema.statement_schema import StatementSchema
from app.domain.repository.fin_repository import (
    delete_financial_statements,
    save_financial_statements
)
from app.domain.service.dart_api_service import DartApiService
from app.domain.service.financial_data_processor import FinancialDataProcessor
from app.domain.service.ratio_service import RatioService
from app.domain.service.company_info_service import CompanyInfoService

logger = logging.getLogger(__name__)

class FinancialStatementService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.dart_api = DartApiService()
        self.data_processor = FinancialDataProcessor()
        self.ratio_service = RatioService(db_session)
        self.company_info_service = CompanyInfoService(db_session)

    async def get_financial_statements(self, company_info: CompanySchema, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """재무제표 데이터를 조회합니다.
        
        Args:
            company_info: 회사 정보
            year: 조회할 연도. None이면 직전 연도의 데이터를 조회
        """
        try:
            statements = await self.dart_api.fetch_financial_statements(company_info.corp_code, year)
            logger.info(f"조회된 재무제표 수: {len(statements)}")
            return statements
        except Exception as e:
            logger.error(f"재무제표 조회 실패: {str(e)}")
            raise

    async def fetch_and_save_financial_data(self, company_name: str, year: Optional[int] = None) -> Dict[str, Any]:
        """회사명으로 재무제표 데이터를 조회하고 저장합니다.
        
        Args:
            company_name: 회사명
            year: 조회할 연도. None이면 직전 연도의 데이터를 조회
        """
        try:
            # 1. 회사 정보 조회
            company_info = await self.company_info_service.get_company_info(company_name)
            
            # 2. 기존 데이터 확인
            existing_data = await self._check_existing_data(company_name, year)
            if existing_data:
                logger.info(f"기존 데이터가 존재합니다: {company_name}, 연도: {year}")
                return {
                    "status": "success",
                    "message": f"{company_name}의 재무제표 데이터가 이미 존재합니다.",
                    "data": existing_data
                }
            
            # 3. 재무제표 데이터 조회
            statements = await self.get_financial_statements(company_info, year)
            
            if not statements:
                return {
                    "status": "error",
                    "message": "재무제표 데이터를 찾을 수 없습니다."
                }
            
            # 4. 중복 제거
            statements = self.data_processor.deduplicate_statements(statements)
            
            # 5. 새로운 데이터 저장
            statement_data = [self.data_processor.prepare_statement_data(stmt, company_info) for stmt in statements]
            await save_financial_statements(self.db_session, statement_data)
            
            # 6. 재무비율 계산 및 저장
            bsns_year = statements[0].get("bsns_year") if statements else None
            if bsns_year:
                await self._calculate_ratios_if_needed(company_info.corp_code, company_info.corp_name, bsns_year)
            
            # 7. 저장된 데이터 조회하여 반환
            saved_data = await self._get_financial_data(company_name, year)
            
            return {
                "status": "success",
                "message": f"{company_name}의 재무제표 데이터가 성공적으로 저장되었습니다.",
                "data": saved_data
            }
            
        except Exception as e:
            logger.error(f"재무제표 데이터 저장 실패: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def _check_existing_data(self, company_name: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """기존 데이터를 확인합니다."""
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
                query = text("""
                    SELECT f.bsns_year, f.sj_div, s.sj_nm, f.account_nm, 
                           f.thstrm_amount, f.frmtrm_amount, f.bfefrmtrm_amount
                    FROM financials f
                    JOIN companies c ON f.corp_code = c.corp_code
                    JOIN statement s ON f.sj_div = s.sj_div
                    WHERE c.corp_name = :company_name
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
            logger.error(f"데이터 확인 중 오류 발생: {str(e)}")
            return []

    async def _get_financial_data(self, company_name: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """저장된 재무제표 데이터를 조회합니다."""
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

    async def _calculate_ratios_if_needed(self, corp_code: str, corp_name: str, bsns_year: str) -> None:
        """재무비율 데이터가 없을 경우 계산하고 저장합니다."""
        try:
            # 기존 재무비율 데이터 확인
            ratio_check_query = text("""
                SELECT 1 FROM metrics 
                WHERE corp_code = :corp_code 
                AND bsns_year = :bsns_year
                LIMIT 1
            """)
            ratio_result = await self.db_session.execute(ratio_check_query, {
                "corp_code": corp_code,
                "bsns_year": bsns_year
            })
            
            # 재무비율 데이터가 없을 때만 계산 및 저장
            if not ratio_result.fetchone():
                await self.ratio_service.calculate_and_save_ratios(
                    corp_code=corp_code,
                    corp_name=corp_name,
                    bsns_year=bsns_year
                )
        except Exception as e:
            logger.error(f"재무비율 계산 확인 중 오류 발생: {str(e)}")

    async def get_formatted_financial_data(self, company_name: str, year: Optional[int] = None) -> Dict[str, Any]:
        """회사명으로 재무제표 데이터를 조회하고 포맷팅하여 반환합니다."""
        try:
            # 데이터 조회
            data = await self.fetch_and_save_financial_data(company_name, year)
            if data["status"] == "error":
                return {
                    "status": "success",
                    "message": "재무제표가 성공적으로 조회되었습니다.",
                    "data": []
                }
            
            # 재무제표 데이터 추출
            financial_data = []
            if data["data"]:
                # 연도별로 데이터 정리
                years_data = {}
                for item in data["data"]:
                    year_str = item["bsns_year"]
                    if year_str not in years_data:
                        years_data[year_str] = {
                            "사업연도": year_str,
                            "재무상태표": {},
                            "손익계산서": {}
                        }
                    
                    # 재무상태표 데이터
                    if item["sj_div"] == "BS":
                        years_data[year_str]["재무상태표"][item["account_nm"]] = {
                            "당기": item["thstrm_amount"],
                            "전기": item["frmtrm_amount"],
                            "전전기": item["bfefrmtrm_amount"]
                        }
                    # 손익계산서 데이터
                    elif item["sj_div"] == "IS":
                        years_data[year_str]["손익계산서"][item["account_nm"]] = {
                            "당기": item["thstrm_amount"],
                            "전기": item["frmtrm_amount"],
                            "전전기": item["bfefrmtrm_amount"]
                        }
                
                # 정렬된 연도 리스트 생성
                sorted_years = sorted(years_data.keys(), reverse=True)
                for year_val in sorted_years:
                    financial_data.append(years_data[year_val])
            
            return {
                "status": "success",
                "message": "재무제표가 성공적으로 조회되었습니다.",
                "data": financial_data
            }
        except Exception as e:
            logger.error(f"재무제표 데이터 포맷팅 실패: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            } 