from pydantic import Field
from app.foundation.infra.database.base_schema import BaseSchema

class ReportSchema(BaseSchema):
    """공시보고서 스키마"""
    rcept_no: str = Field(..., description="접수번호 (공시 문서의 고유 식별자)")
    reprt_code: str = Field(..., description="보고서 코드")
    
    created_at: str = Field(..., description="생성 날짜")
    updated_at: str = Field(..., description="수정 날짜")

    model_config = {
        "from_attributes": True
    } 