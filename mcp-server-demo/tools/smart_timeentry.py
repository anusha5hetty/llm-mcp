import sys
from typing import Any
from mcp.server.fastmcp import FastMCP
from starlette.responses import Response
# from starlette.routing import Mount
from pathlib import Path
PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(PATH))
from utils.http_client import format_strategy_summary, make_api_request, BASE_API_URL, HTTPMethod
from utils.shared_mcp import mcp


@mcp.tool()
async def smart_timeentry(id: str) -> str:
    """Do auto/smart timeentry for the user's Timesheet

    Args: 
        id: structureCode of the strategy
    """
    endpoint = "/internal-api/timesheet/smart-timeentry"
    data = await make_api_request(endpoint, method=HTTPMethod.PUT)

    if not data:
        return f"Unable to reach the endpoint: {endpoint}"
    return {"type": "text", "data": "Time entry completed"}