import sys
from typing import Any, Optional
from mcp.server.fastmcp import FastMCP
from starlette.responses import Response
# from starlette.routing import Mount
from pathlib import Path
PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(PATH))
from utils.http_client import format_strategy_summary, make_api_request, BASE_API_URL, HTTPMethod
from utils.shared_mcp import mcp


@mcp.tool()
async def smart_timeentry(id: str, PF_loginCert: Optional[str] = None) -> str:
    """Do auto/smart timeentry for the user's Timesheet

    Args: 
        id: structureCode of the strategy        
    Note:
        The parameter 'PF_loginCert' is not required from the user. It will be fetched internally by the system.
    """
    endpoint = "/internal-api/timesheet/smart-timeentry"
    cookies = {"LoginCert": PF_loginCert} if PF_loginCert else None
    data = await make_api_request(endpoint, method=HTTPMethod.PUT, cookies=cookies)

    if not data:
        return f"Unable to reach the endpoint: {endpoint}"
    return {"type": "text", "data": "Time entry completed"}