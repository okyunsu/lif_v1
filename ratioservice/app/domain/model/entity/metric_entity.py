from sqlalchemy import TIMESTAMP, Column, Integer, String, Numeric, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class MetricEntity(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, autoincrement=True, doc="자동 증가하는 고유 식별자")
    corp_code = Column(String(20), ForeignKey("companies.corp_code"), nullable=False, doc="기업 코드")
    bsns_year = Column(String(4), nullable=False, doc="사업연도")
    debt_ratio = Column(Numeric, nullable=True, doc="부채비율")
    current_ratio = Column(Numeric, nullable=True, doc="유동비율")
    operating_profit_ratio = Column(Numeric, nullable=True, doc="영업이익률")
    net_profit_ratio = Column(Numeric, nullable=True, doc="순이익률")
    roe = Column(Numeric, nullable=True, doc="자기자본이익률")
    roa = Column(Numeric, nullable=True, doc="총자산이익률")
    debt_dependency = Column(Numeric, nullable=True, doc="부채의존도")
    sales_growth = Column(Numeric, nullable=True, doc="매출성장률")
    operating_profit_growth = Column(Numeric, nullable=True, doc="영업이익성장률")
    eps_growth = Column(Numeric, nullable=True, doc="주당순이익성장률")
    
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), doc="생성 날짜")
    updated_at = Column(TIMESTAMP, nullable=False, doc="수정 날짜")

    # Relationship
    company = relationship("CompanyEntity") 