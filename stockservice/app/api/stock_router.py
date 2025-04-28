from fastapi import APIRouter, Request
import logging

# 로거 설정
logger = logging.getLogger("stock_router")
logger.setLevel(logging.INFO)
router = APIRouter()


# GET
@router.get("/stockservice", summary="모든 회사 주식 정보 조회")
async def get_all_stocks():
    """
    등록된 모든 회사의 주식 정보를 조회합니다.
    """
    print("📋 모든 회사 주식 정보 조회")
    logger.info("📋 모든 회사 주식 정보 조회")
    
    # 샘플 데이터
    companies = [
        {
            "companyName": "샘플전자",
            "stockPrice": 85000,
            "marketCap": 8500000000000,
            "tradingVolume": 1500000,
            "priceToEarnings": 12.5,
            "priceToBook": 1.8,
            "dividendYield": 2.5,
            "year": "2023"
        },
        {
            "companyName": "테스트기업",
            "stockPrice": 75000,
            "marketCap": 7500000000000,
            "tradingVolume": 1200000,
            "priceToEarnings": 15.0,
            "priceToBook": 2.0,
            "dividendYield": 3.0,
            "year": "2023"
        }
    ]
    return {"companies": companies}



# POST

@router.post("/stockservice")
async def get_stock_service(request: Request):
    """
    회사명으로 주식 정보를 조회합니다.
    """
    # 로깅
    print("📈 주식 서비스 호출")
    logger.info("📊 주식 서비스 호출됨")
    
    # 요청 데이터 출력
    try:
        data = await request.json()
        company_name = data.get("company_name", "")
        print(f"회사명: {company_name}")
    except Exception as e:
        print(f"요청 본문 파싱 실패: {e}")
        company_name = ""
    
    if company_name == "샘플전자":
        return {
            "companyName": company_name,
            "stockPrice": 85000,
            "marketCap": 8500000000000,
            "tradingVolume": 1500000,
            "priceToEarnings": 12.5,
            "priceToBook": 1.8,
            "dividendYield": 2.5,
            "year": "2023"
        }
    else:
        return {
            "companyName": "존재하지 않는 회사",
            "stockPrice": 0.0,
            "marketCap": 0.0,
            "tradingVolume": 0.0,
            "priceToEarnings": 0.0,
            "priceToBook": 0.0,
            "dividendYield": 0.0,
            "year": "2023"
        }

# PUT
@router.put("/stockservice", summary="주식 정보 전체 수정")
async def update_stock(request: Request):
    """
    주식 정보를 전체 수정합니다.
    """
    print("📝 주식 정보 전체 수정")
    logger.info("📝 주식 정보 전체 수정")
    
    # 샘플 응답
    return {
        "message": "주식 정보가 성공적으로 수정되었습니다.",
        "updated_data": {
            "companyName": "수정된샘플전자",
            "stockPrice": 90000,
            "marketCap": 9000000000000,
            "tradingVolume": 2000000,
            "priceToEarnings": 13.0,
            "priceToBook": 1.9,
            "dividendYield": 2.8,
            "year": "2023"
        }
    }

# DELETE
@router.delete("/stockservice", summary="주식 정보 삭제")
async def delete_stock():
    """
    주식 정보를 삭제합니다.
    """
    print("🗑️ 주식 정보 삭제")
    logger.info("🗑️ 주식 정보 삭제")
    
    # 샘플 응답
    return {
        "message": "주식 정보가 성공적으로 삭제되었습니다."
    }

# PATCH
@router.patch("/stockservice", summary="주식 정보 부분 수정")
async def patch_stock(request: Request):
    """
    주식 정보를 부분적으로 수정합니다.
    """
    print("✏️ 주식 정보 부분 수정")
    logger.info("✏️ 주식 정보 부분 수정")
    
    # 샘플 응답
    return {
        "message": "주식 정보가 부분적으로 수정되었습니다.",
        "updated_fields": {
            "stockPrice": 88000,
            "tradingVolume": 1800000
        }
    }