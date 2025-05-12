from pydantic import Field
from app.foundation.infra.database.base_schema import BaseSchema

class StatementSchema(BaseSchema):
    """재무제표 구분 스키마"""
    sj_div: str = Field(..., description="재무제표 구분 코드")
    sj_nm: str = Field(..., description="재무제표 구분명")
    
    created_at: str = Field(..., description="생성 날짜")
    updated_at: str = Field(..., description="수정 날짜")

    model_config = {
        "from_attributes": True
    } 