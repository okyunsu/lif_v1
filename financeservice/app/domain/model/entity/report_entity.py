from sqlalchemy import TIMESTAMP, Column, String, func
from app.foundation.infra.database.base import Base

class ReportEntity(Base):
    __tablename__ = "reports"

    rcept_no = Column(String(20), primary_key=True, doc="접수번호 (공시 문서의 고유 식별자)")
    reprt_code = Column(String(20), nullable=False, doc="보고서 코드")
    
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), doc="생성 날짜")
    updated_at = Column(TIMESTAMP, nullable=False, doc="수정 날짜") 