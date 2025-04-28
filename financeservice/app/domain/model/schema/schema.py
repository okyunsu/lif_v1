from pydantic import Field
from typing import List, Optional
from datetime import datetime
from app.foundation.infra.database.base_schema import BaseSchema

# 정규화된 스키마 임포트
from app.domain.model.schema.company_schema import CompanySchema
from app.domain.model.schema.financial_schema import FinancialSchema
from app.domain.model.schema.metric_schema import MetricSchema
from app.domain.model.schema.report_schema import ReportSchema
from app.domain.model.schema.statement_schema import StatementSchema

# DART API 원본 데이터 스키마
class DartApiResponse(BaseSchema):
    """DART API 응답 기본 구조"""
    status: str = Field(..., description="API 응답 상태")
    message: str = Field(..., description="API 응답 메시지")
    list: Optional[List[dict]] = Field(None, description="API 응답 데이터 리스트")

    model_config = {
        "from_attributes": True
    }

class CompanyNameRequest(BaseSchema):
    company_name: str = Field(..., description="회사명")

    model_config = {
        "from_attributes": True
    }

class FinancialMetrics(BaseSchema):
    """재무 지표 데이터"""
    operatingMargin: List[float] = Field(..., description="영업이익률")
    netMargin: List[float] = Field(..., description="순이익률")
    roe: List[float] = Field(..., description="자기자본이익률")
    roa: List[float] = Field(..., description="총자산이익률")
    years: List[str] = Field(..., description="연도 목록 (최근 3개년)")

    model_config = {
        "from_attributes": True
    }

class GrowthData(BaseSchema):
    """성장성 데이터"""
    revenueGrowth: List[float] = Field(..., description="매출액 성장률")
    netIncomeGrowth: List[float] = Field(..., description="순이익 성장률")
    years: List[str] = Field(..., description="연도 목록 (최근 3개년)")

    model_config = {
        "from_attributes": True
    }

class DebtLiquidityData(BaseSchema):
    """부채 및 유동성 데이터"""
    debtRatio: List[float] = Field(..., description="부채비율")
    currentRatio: List[float] = Field(..., description="유동비율")
    years: List[str] = Field(..., description="연도 목록 (최근 3개년)")

    model_config = {
        "from_attributes": True
    }

class FinancialMetricsResponse(BaseSchema):
    """재무제표 응답"""
    companyName: str = Field(..., description="회사명")
    financialMetrics: FinancialMetrics = Field(..., description="재무지표 데이터 (최근 3개년)")
    growthData: GrowthData = Field(..., description="성장성 데이터 (최근 3개년)")
    debtLiquidityData: DebtLiquidityData = Field(..., description="부채 및 유동성 데이터 (최근 3개년)")

    model_config = {
        "from_attributes": True
    }