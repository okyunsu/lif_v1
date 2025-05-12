from typing import Dict, Optional, List
import logging
from .financial_data_processor import FinancialDataProcessor

logger = logging.getLogger(__name__)

class GrowthRateCalculator:
    """성장률 계산 클래스"""
    
    def __init__(self):
        self.data_processor = FinancialDataProcessor()
    
    def calculate_growth_rates(self, years_data: Dict[str, Dict[str, Dict[str, float]]], target_years: List[str]) -> Dict[str, List[Optional[float]]]:
        """매출액과 당기순이익의 성장률을 계산합니다."""
        growth_rates = {
            "revenue_growth": [],
            "net_income_growth": []
        }
        
        for i in range(len(target_years)):
            current_year = target_years[i]
            if i == 0:
                growth_rates["revenue_growth"].append(None)
                growth_rates["net_income_growth"].append(None)
                continue
                
            previous_year = target_years[i-1]
            current_values = self.data_processor.extract_financial_values(years_data.get(current_year, {}), "growth")
            previous_values = self.data_processor.extract_financial_values(years_data.get(previous_year, {}), "growth")
            
            growth_rates["revenue_growth"].append(
                self.calculate_revenue_growth(current_values, previous_values)
            )
            growth_rates["net_income_growth"].append(
                self.calculate_net_income_growth(current_values, previous_values)
            )
        
        return growth_rates

    def calculate_revenue_growth(self, current: Dict[str, float], previous: Dict[str, float]) -> Optional[float]:
        """매출액 성장률을 계산합니다."""
        return self._calculate_growth_rate(current["revenue"], previous["revenue"])

    def calculate_net_income_growth(self, current: Dict[str, float], previous: Dict[str, float]) -> Optional[float]:
        """당기순이익 성장률을 계산합니다."""
        return self._calculate_growth_rate(current["net_income"], previous["net_income"])

    def _calculate_growth_rate(self, current: float, previous: float) -> Optional[float]:
        """성장률을 계산합니다."""
        try:
            if previous == 0:
                return None
            return ((current - previous) / abs(previous)) * 100
        except:
            return None 