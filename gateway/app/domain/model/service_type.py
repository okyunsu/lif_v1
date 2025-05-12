from enum import Enum
import os


class ServiceType(str, Enum):
    FINANCE = "fin"
    ESG = "esg"
    STOCK = "stock"
    RATIO = "ratio"
    
    

# ✅ 환경 변수에서 서비스 URL 가져오기
FINANCE_SERVICE_URL = os.getenv("FINANCE_SERVICE_URL")
ESG_SERVICE_URL = os.getenv("ESG_SERVICE_URL")
STOCK_SERVICE_URL = os.getenv("STOCK_SERVICE_URL")
RATIO_SERVICE_URL = os.getenv("RATIO_SERVICE_URL")

SERVICE_URLS = {
    ServiceType.FINANCE: FINANCE_SERVICE_URL,
    ServiceType.ESG: ESG_SERVICE_URL,
    ServiceType.STOCK: STOCK_SERVICE_URL,
    ServiceType.RATIO: RATIO_SERVICE_URL,
}