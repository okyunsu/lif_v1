from sqlalchemy import TIMESTAMP, Column, String, func
from app.foundation.infra.database.base import Base

class StatementEntity(Base):
    __tablename__ = "statement"

    sj_div = Column(String(10), primary_key=True, doc="재무제표 구분 코드")
    sj_nm = Column(String(100), nullable=False, doc="재무제표 구분명")
    
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), doc="생성 날짜")
    updated_at = Column(TIMESTAMP, nullable=False, doc="수정 날짜") 