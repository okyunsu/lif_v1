from sqlalchemy import TIMESTAMP, Column, Integer, String, Numeric, ForeignKey, func
from sqlalchemy.orm import relationship
from app.foundation.infra.database.base import Base

class FinancialEntity(Base):
    __tablename__ = "financials"

    id = Column(Integer, primary_key=True, autoincrement=True, doc="자동 증가하는 고유 식별자")
    corp_code = Column(String(20), ForeignKey("companies.corp_code"), nullable=False, doc="기업 코드")
    bsns_year = Column(String(4), nullable=False, doc="사업연도")
    sj_div = Column(String(10), ForeignKey("statement.sj_div"), nullable=False, doc="재무제표 구분")
    account_nm = Column(String(100), nullable=False, doc="계정명 (예: 자산총계, 매출액 등)")
    thstrm_nm = Column(String(20), nullable=True, doc="당기명")
    thstrm_amount = Column(Numeric, nullable=True, doc="당기금액")
    frmtrm_nm = Column(String(20), nullable=True, doc="전기명")
    frmtrm_amount = Column(Numeric, nullable=True, doc="전기금액")
    bfefrmtrm_nm = Column(String(20), nullable=True, doc="전전기명")
    bfefrmtrm_amount = Column(Numeric, nullable=True, doc="전전기금액")
    ord = Column(Integer, nullable=True, doc="정렬 순서")
    currency = Column(String(10), nullable=True, doc="통화 단위")
    rcept_no = Column(String(20), ForeignKey("reports.rcept_no"), nullable=True, doc="접수번호")
    
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), doc="생성 날짜")
    updated_at = Column(TIMESTAMP, nullable=False, doc="수정 날짜")

    # Relationships
    company = relationship("CompanyEntity")
    statement = relationship("StatementEntity")
    report = relationship("ReportEntity") 