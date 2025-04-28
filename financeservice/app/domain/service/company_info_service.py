from typing import Dict, Any
import logging
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.service.dart_api_service import DartApiService
from app.domain.model.schema.company_schema import CompanySchema

logger = logging.getLogger(__name__)

class CompanyInfoService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.dart_api = DartApiService()

    async def get_company_info(self, company_name: str) -> CompanySchema:
        """회사 정보를 조회합니다."""
        try:
            # DB에서 먼저 조회
            db_company = await self._get_company_from_db(company_name)
            if db_company:
                # 딕셔너리 키를 CompanySchema 필드와 일치시킴
                company_data = {
                    "corp_code": db_company.get("corp_code", ""),
                    "corp_name": db_company.get("corp_name", company_name),
                    "stock_code": db_company.get("stock_code", ""),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                try:
                    return CompanySchema(**company_data)
                except Exception as e:
                    logger.warning(f"DB 데이터로 CompanySchema 생성 실패: {e}")
            
            # API에서 조회
            dart_company = await self.dart_api.fetch_company_info(company_name)
            
            # CompanyInfo -> CompanySchema로 변환
            return CompanySchema(
                corp_code=dart_company.corp_code,
                corp_name=dart_company.corp_name,
                stock_code=dart_company.stock_code,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"회사 정보 조회 실패: {str(e)}")
            raise

    async def _get_company_from_db(self, company_name: str) -> Dict[str, Any]:
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