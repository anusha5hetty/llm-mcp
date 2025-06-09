from typing import Any
import os
import sys
import argparse
import uvicorn
import asyncio
from mcp.server.fastmcp import FastMCP
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.server.fastmcp.prompts import base
from fastapi import FastAPI, Request
from starlette.responses import Response
from starlette.routing import Mount
from pathlib import Path
PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(PATH))
from utils.http_client import format_strategy_summary, make_api_request, BASE_API_URL, HTTPMethod
from utils.shared_mcp import mcp

@mcp.tool()
async def get_strategy_detail(id: str) -> str:
    """Get Strategy details

    Args: 
        id: structureCode of the strategy
    """
    endpoint = f"/internal-api/strategies/byId/{id}"
    data = await make_api_request(endpoint, method=HTTPMethod.POST)

    if not data:
        return f"Unable to reach the endpoint: {endpoint}"

    description = format_strategy_summary(data)
    return {"description": description}

@mcp.prompt()
def get_initial_prompts() -> list[base.Message]:
    return [
        base.UserMessage("You are a helpful assistant that can help with Portfolio Strategy related questions."),
    ]