import sys
from mcp.server.fastmcp.prompts import base
from pathlib import Path
from typing import Optional

PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(PATH))

from utils.http_client import format_strategy_summary, make_api_request, HTTPMethod
from utils.shared_mcp import mcp, Session

@mcp.tool()
async def get_strategy_detail(
    id: str,
    PF_loginCert: Optional[str] = None
) -> str:
    """
    Get Strategy details.

    Args:
        id: structureCode of the strategy

    Note:
        The parameter 'PF_loginCert' is not required from the user. It will be fetched internally by the system.
    """
    endpoint = f"/internal-api/strategies/byId/{id}"
    Session.login_cert = PF_loginCert
    data = await make_api_request(endpoint, method=HTTPMethod.POST)

    if not data:
        return f"Unable to reach the endpoint: {endpoint}"

    description = format_strategy_summary(data)
    return {"type": "text", "data": description}

@mcp.prompt()
def get_initial_prompts() -> list[base.Message]:
    return [
        base.UserMessage("You are a helpful assistant that can help with Portfolio Strategy related questions."),
    ]