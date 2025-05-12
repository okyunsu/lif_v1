from sqlalchemy import TIMESTAMP, Column, String, func
from app.foundation.infra.database.base import Base

class CompanyEntity(Base):
    __tablename__ = "companies"

    corp_code = Column(String(20), primary_key=True, doc="고유한 기업 코드")
    corp_name = Column(String(100), nullable=False, doc="기업명")
    stock_code = Column(String(20), nullable=True, doc="주식 코드 (상장사인 경우)")
    
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), doc="생성 날짜")
    updated_at = Column(TIMESTAMP, nullable=False, doc="수정 날짜") 