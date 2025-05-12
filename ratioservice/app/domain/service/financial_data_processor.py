from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class FinancialDataProcessor:
    """재무제표 데이터 전처리 클래스"""
    
    def preprocess_financial_data(self, financial_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, float]]]:
        """재무제표 데이터를 전처리합니다."""
        years_data = {}
        
        for item in financial_data:
            year = item["bsns_year"]
            if year not in years_data:
                years_data[year] = {}
            
            account_nm = item["account_nm"]
            years_data[year][account_nm] = {
                "thstrm": float(item["thstrm_amount"]) if item["thstrm_amount"] else 0,
                "frmtrm": float(item["frmtrm_amount"]) if item["frmtrm_amount"] else 0,
                "bfefrmtrm": float(item["bfefrmtrm_amount"]) if item["bfefrmtrm_amount"] else 0
            }
        
        return years_data

    def get_target_years(self, years_data: Dict[str, Dict[str, Dict[str, float]]]) -> List[str]:
        """대상 연도를 결정합니다."""
        all_years = sorted(years_data.keys(), reverse=True)
        return all_years[:3]  # 최근 3개년도만

    def extract_financial_values(self, year_data: Dict[str, Dict[str, float]], values_type: str = "all") -> Dict[str, float]:
        """재무제표 데이터에서 필요한 값을 추출합니다.
        
        Args:
            year_data: 연도별 재무제표 데이터
            values_type: 추출할 값의 타입 ("all", "growth", "ratio")
        """
        base_values = {
            "total_assets": year_data.get("자산총계", {}).get("thstrm", 0),
            "total_liabilities": year_data.get("부채총계", {}).get("thstrm", 0),
            "current_assets": year_data.get("유동자산", {}).get("thstrm", 0),
            "current_liabilities": year_data.get("유동부채", {}).get("thstrm", 0),
            "total_equity": year_data.get("자본총계", {}).get("thstrm", 0),
            "revenue": year_data.get("매출액", {}).get("thstrm", 0),
            "operating_profit": year_data.get("영업이익", {}).get("thstrm", 0),
            "net_income": year_data.get("당기순이익", {}).get("thstrm", 0)
        }
        
        if values_type == "growth":
            return {k: v for k, v in base_values.items() if k in ["revenue", "net_income"]}
        elif values_type == "ratio":
            return base_values
        return base_values 