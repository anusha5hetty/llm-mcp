from enum import Enum
from typing import Any, Optional
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Strategy")

class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    
BASE_API_URL = "http://localhost/planview"
LOGIN_CERT = "Sr-cS8gm8SYC2mBZTyekhD9-r2pNNwzHjJe_V-Xpa"

DEFAULT_HEADERS ={
    "User-Agent": "MyLocalClient/1.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

Default_Cookies = {
    "LoginCert": "Sr-cS8gm8SYC2mBZTyekhD9-r2pNNwzHjJe_V-Xpa"
}

async def make_api_request(
    endpoint: str,
    method: HTTPMethod = HTTPMethod.GET,
    params: Optional[dict[str, Any]] = None,
    body: Optional[dict[str, Any]] = None,
    headers: Optional[dict[str, str]] = None,
    cookies: Optional[dict[str, str]] = None,
    timeout: float = 40.0
) -> Optional[dict[str, Any]]:
    """Make an HTTP request to the configured API endpoint."""
    merged_headers = {**DEFAULT_HEADERS, **(headers or {})}
    merged_cookies = {**Default_Cookies, **(cookies or {})}
    url = f"{BASE_API_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    
    async with httpx.AsyncClient() as client:
        print(f"Making request to {url} with cookies {merged_cookies}")
        try:
            response = await client.request(
                method=method.value,
                url=url,
                headers=merged_headers,
                cookies=merged_cookies,
                params=params,
                json=body if body else None,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"API error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            print(f"Request failed: {e}")
    return None

def format_strategy_summary(strategy: dict[str, Any]) -> str:
    """Create a readable summary from the strategy details."""
    return (
        f"Strategy '{strategy.get('Description', 'N/A')}' "
        f"(ID: {strategy.get('StructureCode', 'N/A')}) is a "
        f"{strategy.get('StrategyType', {}).get('Description', 'N/A')} "
        f"currently in '{strategy.get('Status', {}).get('Description', 'N/A')}'. "
        f"Scheduled from {strategy.get('TargetStart', 'N/A')} to {strategy.get('TargetFinish', 'N/A')}. "
        f"Parent strategy: {strategy.get('Parent', {}).get('Description', 'None')}. "
    )