from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from datetime import datetime
from sqlalchemy import text

from app.domain.model.schema.schema import (
    FinancialMetricsResponse,
    FinancialMetrics,
    GrowthData,
    DebtLiquidityData
)
from app.domain.model.schema.metric_schema import MetricSchema
from app.domain.model.schema.company_schema import CompanySchema
from app.domain.model.schema.financial_schema import FinancialSchema

logger = logging.getLogger(__name__)

class RatioService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    def _safe_divide(self, numerator: float, denominator: float) -> Optional[float]:
        """안전한 나눗셈을 수행합니다."""
        try:
            if denominator == 0:
                return None
            return numerator / denominator
        except:
            return None

    def _calculate_growth_rate(self, current: float, previous: float) -> Optional[float]:
        """성장률을 계산합니다."""
        try:
            if previous == 0:
                # 전기 값이 0인 경우 성장률을 계산할 수 없음
                return None
            
            # 마이너스 값에서 플러스로 전환된 경우나 플러스에서 마이너스로 전환된 경우를 고려
            if previous < 0 and current > 0:
                # 마이너스에서 플러스로 전환된 경우
                return 100.0
            elif previous > 0 and current < 0:
                # 플러스에서 마이너스로 전환된 경우
                return -100.0
            
            return ((current - previous) / abs(previous)) * 100
        except (ZeroDivisionError, TypeError):
            return None

    async def calculate_and_save_ratios(self, corp_code: str, corp_name: str, bsns_year: Optional[str] = None) -> Dict[str, Any]:
        """재무비율을 계산하고 저장합니다."""
        try:
            # 재무제표 데이터 조회
            base_query = """
                SELECT 
                    f.account_nm, 
                    f.thstrm_amount, 
                    f.frmtrm_amount,
                    f.bfefrmtrm_amount,
                    f.bsns_year
                FROM financials f
                WHERE f.corp_code = :corp_code
                AND f.sj_div IN ('BS', 'IS')  -- 재무상태표와 손익계산서만 조회
            """
            
            if bsns_year:
                query = text(base_query + " AND f.bsns_year = :bsns_year ORDER BY f.sj_div, f.ord")
                result = await self.db_session.execute(query, {
                    "corp_code": corp_code,
                    "bsns_year": bsns_year
                })
            else:
                # 최근 3개년도 데이터 조회
                query = text(base_query + """
                    AND f.bsns_year IN (
                        SELECT DISTINCT bsns_year 
                        FROM financials 
                        WHERE corp_code = :corp_code 
                        ORDER BY bsns_year DESC 
                        LIMIT 3
                    )
                    ORDER BY f.bsns_year DESC, f.sj_div, f.ord
                """)
                result = await self.db_session.execute(query, {"corp_code": corp_code})
            
            # 계정과목별 금액을 딕셔너리로 변환
            financial_data = {}
            current_year = None
            
            for row in result:
                year = row[4]  # bsns_year
                if current_year is None:
                    current_year = year
                
                if year not in financial_data:
                    financial_data[year] = {}
                
                financial_data[year][row[0]] = {  # account_nm
                    'thstrm': float(row[1]) if row[1] is not None else 0,  # thstrm_amount
                    'frmtrm': float(row[2]) if row[2] is not None else 0,  # frmtrm_amount
                    'bfefrmtrm': float(row[3]) if row[3] is not None else 0  # bfefrmtrm_amount
                }

            # 각 연도별로 재무비율 계산 및 저장
            all_ratios = {}
            for year, year_data in financial_data.items():
                ratios = self._calculate_ratios(year_data)
                all_ratios[year] = ratios
                
                # 재무비율 저장
                await self._save_ratios_to_db(corp_code, year, ratios)
            
            await self.db_session.commit()
            
            # 현재 연도의 비율 반환
            return all_ratios.get(current_year, {}) if current_year else {}
            
        except Exception as e:
            logger.error(f"재무비율 계산 및 저장 실패: {str(e)}")
            await self.db_session.rollback()
            raise

    async def _save_ratios_to_db(self, corp_code: str, bsns_year: str, ratios: Dict[str, Optional[float]]) -> None:
        """계산된 재무비율을 DB에 저장합니다."""
        metrics = [
            {"metric_name": "debt_ratio", "value": ratios.get("debt_ratio")},
            {"metric_name": "current_ratio", "value": ratios.get("current_ratio")},
            {"metric_name": "operating_profit_ratio", "value": ratios.get("operating_profit_ratio")},
            {"metric_name": "net_profit_ratio", "value": ratios.get("net_profit_ratio")},
            {"metric_name": "roe", "value": ratios.get("roe")},
            {"metric_name": "roa", "value": ratios.get("roa")},
            {"metric_name": "debt_dependency", "value": ratios.get("debt_dependency")},
            {"metric_name": "sales_growth", "value": ratios.get("sales_growth")},
            {"metric_name": "operating_profit_growth", "value": ratios.get("operating_profit_growth")},
            {"metric_name": "eps_growth", "value": ratios.get("eps_growth")}
        ]
        
        # 각 지표별로 저장 또는 업데이트
        for metric in metrics:
            if metric["value"] is not None:
                insert_query = text("""
                    INSERT INTO metrics (
                        corp_code, bsns_year, metric_name, metric_value, metric_unit
                    ) VALUES (
                        :corp_code, :bsns_year, :metric_name, :metric_value, '%'
                    )
                    ON CONFLICT (corp_code, bsns_year, metric_name) DO UPDATE SET
                        metric_value = EXCLUDED.metric_value,
                        updated_at = CURRENT_TIMESTAMP
                """)
                
                await self.db_session.execute(insert_query, {
                    "corp_code": corp_code,
                    "bsns_year": bsns_year,
                    "metric_name": metric["metric_name"],
                    "metric_value": metric["value"]
                })

    def _calculate_ratios(self, year_data: Dict[str, Dict[str, float]]) -> Dict[str, Optional[float]]:
        """재무비율을 계산합니다."""
        try:
            # 필요한 계정과목 금액 추출
            total_assets = year_data.get('자산총계', {}).get('thstrm', 0)
            total_liabilities = year_data.get('부채총계', {}).get('thstrm', 0)
            current_assets = year_data.get('유동자산', {}).get('thstrm', 0)
            current_liabilities = year_data.get('유동부채', {}).get('thstrm', 0)
            total_equity = year_data.get('자본총계', {}).get('thstrm', 0)
            revenue = year_data.get('매출액', {}).get('thstrm', 0)
            operating_profit = year_data.get('영업이익', {}).get('thstrm', 0)
            net_income = year_data.get('당기순이익', {}).get('thstrm', 0)
            
            # 전기 데이터
            prev_revenue = year_data.get('매출액', {}).get('frmtrm', 0)
            prev_operating_profit = year_data.get('영업이익', {}).get('frmtrm', 0)
            prev_net_income = year_data.get('당기순이익', {}).get('frmtrm', 0)
            
            # 재무비율 계산
            ratios = {
                # 안정성 비율
                "debt_ratio": self._safe_divide(total_liabilities, total_equity) * 100 if total_equity != 0 else None,
                "current_ratio": self._safe_divide(current_assets, current_liabilities) * 100 if current_liabilities != 0 else None,
                "debt_dependency": self._safe_divide(total_liabilities, total_assets) * 100 if total_assets != 0 else None,
                
                # 수익성 비율
                "operating_profit_ratio": self._safe_divide(operating_profit, revenue) * 100 if revenue != 0 else None,
                "net_profit_ratio": self._safe_divide(net_income, revenue) * 100 if revenue != 0 else None,
                "roe": self._safe_divide(net_income, total_equity) * 100 if total_equity != 0 else None,
                "roa": self._safe_divide(net_income, total_assets) * 100 if total_assets != 0 else None,
                
                # 성장성 비율
                "sales_growth": self._calculate_growth_rate(revenue, prev_revenue),
                "operating_profit_growth": self._calculate_growth_rate(operating_profit, prev_operating_profit),
                "eps_growth": self._calculate_growth_rate(net_income, prev_net_income)
            }
            
            return ratios
            
        except Exception as e:
            logger.error(f"재무비율 계산 중 오류 발생: {str(e)}")
            raise

    async def get_financial_metrics(self, corp_code: str, company_name: str, financial_data: List[Dict[str, Any]]) -> FinancialMetricsResponse:
        """여러 연도의 재무 지표를 계산하고 반환합니다."""
        try:
            # 연도별 데이터 분류
            years_data = {}
            
            # 모든 연도 수집
            all_years = set()
            for item in financial_data:
                all_years.add(item["bsns_year"])
                
                # 계정과목별 데이터 구성
                year = item["bsns_year"]
                if year not in years_data:
                    years_data[year] = {}
                
                account_nm = item["account_nm"]
                if account_nm not in years_data[year]:
                    years_data[year][account_nm] = {
                        "thstrm": float(item["thstrm_amount"]) if item["thstrm_amount"] else 0,
                        "frmtrm": float(item["frmtrm_amount"]) if item["frmtrm_amount"] else 0,
                        "bfefrmtrm": float(item["bfefrmtrm_amount"]) if item["bfefrmtrm_amount"] else 0
                    }
            
            if not years_data:
                return self._empty_metrics_response(company_name)
            
            # 연도 정렬 (최신순)
            sorted_years = sorted(all_years, reverse=True)
            years = sorted_years[:3]  # 최근 3개년도만
            
            # 각 연도별 당기, 전기, 전전기 데이터 모두 수집하기
            all_year_data = {}
            for year in years:
                # 당해년도 데이터
                if year in years_data:
                    all_year_data[year] = years_data[year]
                
                # 해당 연도의 보고서에 있는 전기 데이터 이용
                prev_year = str(int(year) - 1)
                if prev_year not in all_year_data:
                    all_year_data[prev_year] = {}
                    
                    # 당해년도 데이터에서 전기 데이터 추출
                    for account_nm, values in years_data.get(year, {}).items():
                        all_year_data[prev_year][account_nm] = {
                            "thstrm": values.get("frmtrm", 0)
                        }
                
                # 해당 연도의 보고서에 있는 전전기 데이터 이용
                prev_prev_year = str(int(year) - 2)
                if prev_prev_year not in all_year_data:
                    all_year_data[prev_prev_year] = {}
                    
                    # 당해년도 데이터에서 전전기 데이터 추출
                    for account_nm, values in years_data.get(year, {}).items():
                        all_year_data[prev_prev_year][account_nm] = {
                            "thstrm": values.get("bfefrmtrm", 0)
                        }
            
            # 재정렬하여 최근 3개년만 선택
            full_years = sorted(all_year_data.keys(), reverse=True)
            target_years = full_years[:3]
            
            # 각 연도별 재무비율 계산
            operating_margins, net_margins = [], []
            roe_values, roa_values = [], []
            debt_ratios, current_ratios = [], []
            
            for year in target_years:
                if year in all_year_data:
                    year_data = all_year_data[year]
                    
                    # 계산에 필요한 데이터 추출
                    total_assets = 0
                    total_liabilities = 0
                    current_assets = 0
                    current_liabilities = 0
                    total_equity = 0
                    revenue = 0
                    operating_profit = 0
                    net_income = 0
                    
                    # 재무상태표 데이터
                    for account_nm, values in year_data.items():
                        if account_nm == "자산총계":
                            total_assets = values.get("thstrm", 0)
                        elif account_nm == "부채총계":
                            total_liabilities = values.get("thstrm", 0)
                        elif account_nm == "유동자산":
                            current_assets = values.get("thstrm", 0)
                        elif account_nm == "유동부채":
                            current_liabilities = values.get("thstrm", 0)
                        elif account_nm == "자본총계":
                            total_equity = values.get("thstrm", 0)
                        elif account_nm == "매출액":
                            revenue = values.get("thstrm", 0)
                        elif account_nm == "영업이익":
                            operating_profit = values.get("thstrm", 0)
                        elif account_nm == "당기순이익":
                            net_income = values.get("thstrm", 0)
                    
                    # 재무비율 계산
                    if revenue != 0:
                        operating_margins.append(operating_profit / revenue * 100)
                        net_margins.append(net_income / revenue * 100)
                    else:
                        operating_margins.append(None)
                        net_margins.append(None)
                    
                    if total_equity != 0:
                        roe_values.append(net_income / total_equity * 100)
                        debt_ratios.append(total_liabilities / total_equity * 100)
                    else:
                        roe_values.append(None)
                        debt_ratios.append(None)
                    
                    if total_assets != 0:
                        roa_values.append(net_income / total_assets * 100)
                    else:
                        roa_values.append(None)
                    
                    if current_liabilities != 0:
                        current_ratios.append(current_assets / current_liabilities * 100)
                    else:
                        current_ratios.append(None)
                else:
                    # 데이터가 없는 연도는 None으로 채움
                    operating_margins.append(None)
                    net_margins.append(None)
                    roe_values.append(None)
                    roa_values.append(None)
                    debt_ratios.append(None)
                    current_ratios.append(None)
            
            # 성장률 계산 (당해와 전기 비교)
            revenue_growths, net_income_growths = [], []
            for i in range(len(target_years) - 1):
                current_year = target_years[i]
                prev_year = target_years[i + 1]
                
                if current_year in all_year_data and prev_year in all_year_data:
                    # 당해년도 데이터
                    current_revenue = 0
                    current_income = 0
                    for account_nm, values in all_year_data[current_year].items():
                        if account_nm == "매출액":
                            current_revenue = values.get("thstrm", 0)
                        elif account_nm == "당기순이익":
                            current_income = values.get("thstrm", 0)
                    
                    # 전년도 데이터
                    prev_revenue = 0
                    prev_income = 0
                    for account_nm, values in all_year_data[prev_year].items():
                        if account_nm == "매출액":
                            prev_revenue = values.get("thstrm", 0)
                        elif account_nm == "당기순이익":
                            prev_income = values.get("thstrm", 0)
                    
                    # 성장률 계산
                    if prev_revenue != 0:
                        revenue_growths.append(self._calculate_growth_rate(current_revenue, prev_revenue))
                    else:
                        revenue_growths.append(None)
                    
                    if prev_income != 0:
                        net_income_growths.append(self._calculate_growth_rate(current_income, prev_income))
                    else:
                        net_income_growths.append(None)
                else:
                    revenue_growths.append(None)
                    net_income_growths.append(None)
            
            return FinancialMetricsResponse(
                companyName=company_name,
                financialMetrics=FinancialMetrics(
                    operatingMargin=operating_margins,
                    netMargin=net_margins,
                    roe=roe_values,
                    roa=roa_values,
                    years=target_years
                ),
                growthData=GrowthData(
                    revenueGrowth=revenue_growths,
                    netIncomeGrowth=net_income_growths,
                    years=target_years[:-1]  # 성장률은 마지막 연도 제외
                ),
                debtLiquidityData=DebtLiquidityData(
                    debtRatio=debt_ratios,
                    currentRatio=current_ratios,
                    years=target_years
                )
            )
            
        except Exception as e:
            logger.error(f"재무 지표 계산 중 오류 발생: {str(e)}")
            raise 

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