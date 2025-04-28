from datetime import datetime
from typing import Optional
from app.foundation.infra.database.base_schema import BaseSchema

class FinancialSchema(BaseSchema):
    """재무제표 스키마"""
    id: Optional[int] = None
    corp_code: str
    bsns_year: str
    sj_div: str
    account_nm: str
    thstrm_nm: Optional[str] = None
    thstrm_amount: Optional[float] = None
    frmtrm_nm: Optional[str] = None
    frmtrm_amount: Optional[float] = None
    bfefrmtrm_nm: Optional[str] = None
    bfefrmtrm_amount: Optional[float] = None
    ord: Optional[int] = None
    currency: Optional[str] = None
    rcept_no: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    } 

