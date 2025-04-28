from typing import Optional
from fastapi import HTTPException
import httpx
from app.domain.model.service_type import SERVICE_URLS, ServiceType

class ServiceProxyFactory:
    def __init__(self, service_type: ServiceType):
        self.base_url = SERVICE_URLS[service_type]
        print(f"🔍 Service URL: {self.base_url}")
    async def request(
        self,
        method: str,
        path: str,
        headers: list[tuple[bytes, bytes]],
        body: Optional[bytes] = None
    ) -> httpx.Response:
        if path == "financial":
            path = "fin/financial"
        elif path == "stockservice":
            path = "stock/stockservice"
        elif path == "esgservice":
            path = "esg/esgservice"
        url = f"{self.base_url}/{path}"
        print(f"🔍 Requesting URL: {url}")
        # 헤더 설정
        headers_dict = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers_dict,
                    content=body
                )
                print(f"Response status: {response.status_code}")
                print(f"Request URL: {url}")
                print(f"Request body: {body}")
                return response
            except Exception as e:
                print(f"Request failed: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))