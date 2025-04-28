import os
import logging
import aiohttp
import zipfile
import xml.etree.ElementTree as ET
from io import BytesIO
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from datetime import datetime

from app.domain.model.schema.schema import DartApiResponse
from app.domain.model.schema.company_schema import CompanySchema
from app.domain.model.schema.report_schema import ReportSchema
from app.domain.model.schema.financial_schema import FinancialSchema
from app.domain.model.schema.statement_schema import StatementSchema

# 로깅 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 핸들러가 없으면 추가
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

class DartApiService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("DART_API_KEY")
        if not self.api_key:
            logger.error("DART API 키가 필요합니다.")
            raise ValueError("DART API 키가 필요합니다.")
        logger.info("DartApiService가 초기화되었습니다.")

    async def fetch_company_info(self, company_name: str) -> CompanySchema:
        """DART API에서 회사 정보를 조회합니다."""
        logger.info(f"회사 정보 조회 시작: {company_name}")
        url = "https://opendart.fss.or.kr/api/corpCode.xml"
        params = {"crtfc_key": self.api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"API 요청 실패: {response.status}")
                    raise Exception(f"API 요청 실패: {response.status}")
                
                content = await response.read()
                with zipfile.ZipFile(BytesIO(content)) as zip_file:
                    with zip_file.open('CORPCODE.xml') as xml_file:
                        tree = ET.parse(xml_file)
                        root = tree.getroot()
                        
                        for company in root.findall('.//list'):
                            if company.findtext('corp_name') == company_name:
                                logger.info(f"회사 정보를 찾았습니다: {company_name}")
                                now = datetime.now().isoformat()
                                return CompanySchema(
                                    corp_code=company.findtext('corp_code'),
                                    corp_name=company_name,
                                    stock_code=company.findtext('stock_code') or "",
                                    created_at=now,
                                    updated_at=now
                                )
                        
                        logger.error(f"회사명 '{company_name}'을 찾을 수 없습니다.")
                        raise ValueError(f"회사명 '{company_name}'을 찾을 수 없습니다.")

    def _prepare_financial_data(self, raw_data: Dict[str, Any]) -> FinancialSchema:
        """API 응답 데이터에서 재무제표 스키마 객체를 생성합니다."""
        try:
            return FinancialSchema(
                corp_code=raw_data.get("corp_code", ""),
                bsns_year=raw_data.get("bsns_year", ""),
                sj_div=raw_data.get("sj_div", ""),
                account_nm=raw_data.get("account_nm", ""),
                thstrm_nm=raw_data.get("thstrm_nm", ""),
                thstrm_amount=float(raw_data.get("thstrm_amount", 0)) if raw_data.get("thstrm_amount") else None,
                frmtrm_nm=raw_data.get("frmtrm_nm", ""),
                frmtrm_amount=float(raw_data.get("frmtrm_amount", 0)) if raw_data.get("frmtrm_amount") else None,
                bfefrmtrm_nm=raw_data.get("bfefrmtrm_nm", ""),
                bfefrmtrm_amount=float(raw_data.get("bfefrmtrm_amount", 0)) if raw_data.get("bfefrmtrm_amount") else None,
                ord=int(raw_data.get("ord", 0)),
                currency=raw_data.get("currency", ""),
                rcept_no=raw_data.get("rcept_no", ""),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        except Exception as e:
            logger.error(f"재무제표 데이터 변환 실패: {str(e)}")
            raise

    async def fetch_financial_statements(self, corp_code: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """DART API에서 재무제표 데이터를 조회합니다.
        
        Args:
            corp_code: 회사 코드
            year: 조회할 연도. None이면 직전 연도의 데이터를 조회
        """
        logger.info(f"재무제표 조회 시작 - corp_code: {corp_code}, year: {year}")
        statements = []
        current_year = datetime.now().year
        
        # 연도 설정
        if year is None or not isinstance(year, int):
            target_year = current_year - 1
            logger.info(f"연도가 지정되지 않아 {target_year}년도 데이터를 조회합니다.")
        else:
            target_year = year
            logger.info(f"{target_year}년도 데이터를 조회합니다.")
        
        # 사업보고서만 조회
        report_codes = [("11011", "사업보고서")]
        
        for reprt_code, reprt_name in report_codes:
            url = "https://opendart.fss.or.kr/api/fnlttSinglAcnt.json"
            params = {
                "crtfc_key": self.api_key,
                "corp_code": corp_code,
                "bsns_year": str(target_year),
                "reprt_code": reprt_code,
                "fs_div": "CFS"
            }
            
            logger.info(f"{target_year}년도 {reprt_name} 조회를 시작합니다.")
            
            async with aiohttp.ClientSession() as session:
                # 재무상태표와 손익계산서 조회
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"{reprt_name} API 요청 실패: {response.status}")
                        continue
                        
                    data = await response.json()
                    api_response = DartApiResponse(**data)
                    
                    if api_response.status != "000":
                        logger.error(f"{target_year}년도 {reprt_name} API 응답 실패: {api_response.message}")
                        if year is None and target_year > current_year - 3:
                            # 직전 연도 데이터도 없으면 그 이전 연도 시도
                            logger.info(f"직전 연도({target_year}) 데이터가 없어 이전 연도({target_year-1}) 조회를 시도합니다.")
                            return await self.fetch_financial_statements(corp_code, target_year - 1)
                        continue
                    
                    for item in api_response.list:
                        if item.get("sj_div") in ["BS", "IS"]:
                            item["thstrm_nm"] = f"{int(item['bsns_year'])}년"
                            item["frmtrm_nm"] = f"{int(item['bsns_year'])-1}년"
                            item["bfefrmtrm_nm"] = f"{int(item['bsns_year'])-2}년"
                            statements.append(item)
                
                # 현금흐름표 조회
                cf_url = "https://opendart.fss.or.kr/api/fnlttCashFlow.json"
                async with session.get(cf_url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"{reprt_name} 현금흐름표 API 요청 실패: {response.status}")
                        continue
                        
                    data = await response.json()
                    api_response = DartApiResponse(**data)
                    
                    if api_response.status != "000":
                        logger.error(f"{target_year}년도 {reprt_name} 현금흐름표 API 응답 실패: {api_response.message}")
                        continue
                    
                    for item in api_response.list:
                        item["sj_div"] = "CF"
                        item["sj_nm"] = "현금흐름표"
                        item["thstrm_nm"] = f"{int(item['bsns_year'])}년"
                        item["frmtrm_nm"] = f"{int(item['bsns_year'])-1}년"
                        item["bfefrmtrm_nm"] = f"{int(item['bsns_year'])-2}년"
                        statements.append(item)
                
                # 데이터를 찾았다면 더 이상 시도하지 않음
                if statements:
                    logger.info(f"{target_year}년도 {reprt_name}에서 재무제표 데이터를 찾았습니다.")
                    break
        
        logger.info(f"조회된 재무제표 수: {len(statements)}")
        return statements 