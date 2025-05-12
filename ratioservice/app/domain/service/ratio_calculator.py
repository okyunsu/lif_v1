from typing import Dict, Optional, List
import logging
from .financial_data_processor import FinancialDataProcessor

logger = logging.getLogger(__name__)

class RatioCalculator:
    """재무비율 계산 클래스"""
    
    def __init__(self):
        self.data_processor = FinancialDataProcessor()
    
    def calculate_all_ratios(self, years_data: Dict[str, Dict[str, Dict[str, float]]], target_years: List[str]) -> Dict[str, List[Optional[float]]]:
        """모든 재무비율을 계산합니다."""
        ratios = {
            "operating_margins": [],
            "net_margins": [],
            "roe_values": [],
            "roa_values": [],
            "debt_ratios": [],
            "current_ratios": []
        }
        
        for year in target_years:
            year_data = years_data.get(year, {})
            financial_values = self.data_processor.extract_financial_values(year_data, "ratio")
            
            ratios["operating_margins"].append(self.calculate_operating_margin(financial_values))
            ratios["net_margins"].append(self.calculate_net_margin(financial_values))
            ratios["roe_values"].append(self.calculate_roe(financial_values))
            ratios["roa_values"].append(self.calculate_roa(financial_values))
            ratios["debt_ratios"].append(self.calculate_debt_ratio(financial_values))
            ratios["current_ratios"].append(self.calculate_current_ratio(financial_values))
        
        return ratios

    def calculate_operating_margin(self, values: Dict[str, float]) -> Optional[float]:
        """영업이익률을 계산합니다."""
        return self._safe_divide(values["operating_profit"], values["revenue"]) * 100

    def calculate_net_margin(self, values: Dict[str, float]) -> Optional[float]:
        """순이익률을 계산합니다."""
        return self._safe_divide(values["net_income"], values["revenue"]) * 100

    def calculate_roe(self, values: Dict[str, float]) -> Optional[float]:
        """ROE를 계산합니다."""
        return self._safe_divide(values["net_income"], values["total_equity"]) * 100

    def calculate_roa(self, values: Dict[str, float]) -> Optional[float]:
        """ROA를 계산합니다."""
        return self._safe_divide(values["net_income"], values["total_assets"]) * 100

    def calculate_debt_ratio(self, values: Dict[str, float]) -> Optional[float]:
        """부채비율을 계산합니다."""
        return self._safe_divide(values["total_liabilities"], values["total_equity"]) * 100

    def calculate_current_ratio(self, values: Dict[str, float]) -> Optional[float]:
        """유동비율을 계산합니다."""
        return self._safe_divide(values["current_assets"], values["current_liabilities"]) * 100

    def _safe_divide(self, numerator: float, denominator: float) -> Optional[float]:
        """안전한 나눗셈을 수행합니다."""
        try:
            if denominator == 0:
                return None
            return numerator / denominator
        except:
            return None 