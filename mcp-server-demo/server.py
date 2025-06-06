# server.py
from mcp.server.fastmcp import FastMCP
from typing import Dict
# Create an MCP server
mcp = FastMCP("Demo")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> Dict[str, int]:
    """Add two numbers"""
    return {"type": "redirect", "value": a+b}

@mcp.tool()
def substract(a: int, b: int) -> int:
    """Substract two numbers"""
    return a - b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run()