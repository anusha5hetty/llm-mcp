# server.py
from typing import Dict
from utils.shared_mcp import mcp
from starlette.responses import Response

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> Dict[str, int]:
    """Add two numbers"""
    return {"type": "text", "data": a+b}


@mcp.tool()
def substract(a: int, b: int) -> int:
    """Substract two numbers"""
    return {"type": "text", "data": a-b}

@mcp.tool()
def sample_redirect_url(url: str) -> str:
    """Redirect to a url"""
    return {"type": "redirect", "data": url}

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"
