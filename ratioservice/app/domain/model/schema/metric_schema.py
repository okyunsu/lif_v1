from typing import List
from pydantic import Field
from app.foundation.infra.database.base_schema import BaseSchema

class MetricSchema(BaseSchema):
    """재무지표 스키마"""
    id: int = Field(..., description="자동 증가하는 고유 식별자")
    corp_code: str = Field(..., description="기업 코드")
    bsns_year: str = Field(..., description="사업연도")
    metric_name: str = Field(..., description="지표명")
    metric_value: float = Field(..., description="지표값")
    metric_unit: str | None = Field(None, description="지표 단위")
    
    created_at: str = Field(..., description="생성 날짜")
    updated_at: str = Field(..., description="수정 날짜")

    model_config = {
        "from_attributes": True
    } 


