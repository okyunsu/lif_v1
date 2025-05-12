from typing import Dict, List, Optional
from app.domain.model.schema.schema import FinancialMetricsResponse, FinancialMetrics, GrowthData, DebtLiquidityData
import logging
import math

logger = logging.getLogger(__name__)

def to_float_list(lst, n):
    # None, NaN, 잘못된 값이 있으면 0.0으로 변환, 길이 안 맞으면 빈 리스트
    if not isinstance(lst, list) or len(lst) != n:
        return [0.0] * n
    result = []
    for x in lst:
        try:
            if x is None or (isinstance(x, float) and math.isnan(x)):
                result.append(0.0)
            else:
                result.append(float(x))
        except Exception:
            result.append(0.0)
    return result

class ResponseBuilder:
    """응답 생성 클래스"""
    
    def build_metrics_response(
        self,
        company_name: str,
        target_years: List[str],
        ratios: Dict[str, List[Optional[float]]],
        growth_rates: Dict[str, List[Optional[float]]]
    ) -> FinancialMetricsResponse:
        """재무비율 응답을 생성합니다."""
        n = len(target_years)
        revenue_growth = to_float_list(growth_rates.get("revenue_growth"), n)
        net_income_growth = to_float_list(growth_rates.get("net_income_growth"), n)
        debt_ratios = to_float_list(ratios.get("debt_ratios"), n)
        current_ratios = to_float_list(ratios.get("current_ratios"), n)
        operating_margins = to_float_list(ratios.get("operating_margins"), n)
        net_margins = to_float_list(ratios.get("net_margins"), n)
        roe_values = to_float_list(ratios.get("roe_values"), n)
        roa_values = to_float_list(ratios.get("roa_values"), n)

        metrics = FinancialMetrics(
            operatingMargin=operating_margins,
            netMargin=net_margins,
            roe=roe_values,
            roa=roa_values,
            years=target_years
        )
        growth = GrowthData(
            revenueGrowth=revenue_growth,
            netIncomeGrowth=net_income_growth,
            years=target_years
        )
        debt_liquidity = DebtLiquidityData(
            debtRatio=debt_ratios,
            currentRatio=current_ratios,
            years=target_years
        )
        return FinancialMetricsResponse(
            companyName=company_name,
            financialMetrics=metrics,
            growthData=growth,
            debtLiquidityData=debt_liquidity
        ) 