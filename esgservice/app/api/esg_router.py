from fastapi import APIRouter, Request
import logging

# 로거 설정
logger = logging.getLogger("esg_router")
logger.setLevel(logging.INFO)
router = APIRouter()



# GET
@router.get("/esgservice", summary="모든 회사 ESG 정보 조회")
async def get_all_esg():
    """
    등록된 모든 회사의 ESG 정보를 조회합니다.
    """
    print("📋 모든 회사 ESG 정보 조회")
    logger.info("📋 모든 회사 ESG 정보 조회")
    
    # 샘플 데이터
    companies = [
        {
            "companyName": "샘플전자",
            "esgScore": 85.5,
            "environmental": "A+",
            "social": "A-",
            "governance": "A-",
            "year": "2023"
        },
        {
            "companyName": "테스트기업",
            "esgScore": 75.0,
            "environmental": "B+",
            "social": "B",
            "governance": "B+",
            "year": "2023"
        }
    ]
    return {"companies": companies}



# POST
@router.post("/esgservice")
async def get_esg_service(request: Request):
    """
    회사명으로 ESG 정보를 조회합니다.
    """
    # 로깅
    print("🔥 ESG 서비스 호출")
    logger.info("🌿 ESG 서비스 호출됨")
    
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
            "esgScore": 85.5,
            "environmental": "A+",
            "social": "A-",
            "governance": "A-",
            "year": "2023"
        }
    else:
        return {
            "companyName": "존재하지 않는 회사",
            "esgScore": 0.0,
            "environmental": "N/A",
            "social": "N/A",
            "governance": "N/A",
            "year": "2023"
        }

# PUT
@router.put("/esgservice", summary="ESG 정보 전체 수정")
async def update_esg(request: Request):
    """
    ESG 정보를 전체 수정합니다.
    """
    print("📝 ESG 정보 전체 수정")
    logger.info("📝 ESG 정보 전체 수정")
    
    # 샘플 응답
    return {
        "message": "ESG 정보가 성공적으로 수정되었습니다.",
        "updated_data": {
            "companyName": "수정된샘플전자",
            "esgScore": 90.0,
            "environmental": "A+",
            "social": "A+",
            "governance": "A+",
            "year": "2023"
        }
    }

# DELETE
@router.delete("/esgservice", summary="ESG 정보 삭제")
async def delete_esg():
    """
    ESG 정보를 삭제합니다.
    """
    print("🗑️ ESG 정보 삭제")
    logger.info("🗑️ ESG 정보 삭제")
    
    # 샘플 응답
    return {
        "message": "ESG 정보가 성공적으로 삭제되었습니다."
    }

# PATCH
@router.patch("/esgservice", summary="ESG 정보 부분 수정")
async def patch_esg(request: Request):
    """
    ESG 정보를 부분적으로 수정합니다.
    """
    print("✏️ ESG 정보 부분 수정")
    logger.info("✏️ ESG 정보 부분 수정")
    
    # 샘플 응답
    return {
        "message": "ESG 정보가 부분적으로 수정되었습니다.",
        "updated_fields": {
            "esgScore": 88.0,
            "environmental": "A+"
        }
    }
