from pydantic import Field
from app.foundation.infra.database.base_schema import BaseSchema

class CompanySchema(BaseSchema):
    """기업 정보 스키마"""
    corp_code: str = Field(..., description="고유한 기업 코드")
    corp_name: str = Field(..., description="기업명")
    stock_code: str | None = Field(None, description="주식 코드 (상장사인 경우)")
    
    created_at: str = Field(..., description="생성 날짜")
    updated_at: str = Field(..., description="수정 날짜")

    model_config = {
        "from_attributes": True
    } 

