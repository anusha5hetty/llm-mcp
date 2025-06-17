import os
import sys
import argparse
import importlib
from pathlib import Path
import pkgutil
import uvicorn
import asyncio
from fastmcp import FastMCP

PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(PATH))

from utils.fastapi_factory import build_mcp_fastapi_app
from utils.shared_mcp import set_mcp, Session, mcp


def discover_tool_modules() -> list[str]:
    """Auto-discovers all mcp tools in tools/ folder."""
    tools_dir = Path(__file__).parent / "tools"
    return [
        name for _, name, _ in pkgutil.iter_modules([str(tools_dir)])
        if not name.startswith("__")
    ]

def load_tool_module(module_name: str):
    """Dynamically import and return the tool module."""
    return importlib.import_module(f"tools.{module_name}")

async def print_registered_tools(mcp):
    tools = await mcp.list_tools()
    print("[MCP] Available tools:")
    for t in tools:
        print("-", t.name)

def main():
    parser = argparse.ArgumentParser(description="Run Portfolio MCP server")
    parser.add_argument("--tools", nargs="+", help="Tool module names to load (default: all tools in /tools)")
    parser.add_argument("--mode", choices=["sse", "stdio", "http"], default=os.getenv("MCP_MODE", "sse"))
    parser.add_argument("--login_cert")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    tool_modules = args.tools if args.tools else discover_tool_modules()
    Session.login_cert = args.login_cert

    # Step 1: Load the tool module
    try:
        for tool in tool_modules:
            load_tool_module(tool)
    except Exception as e:
        print(f"❌ Failed to load tool(s)': {e}")
        return

    # Step 2: Run based on mode
    if args.mode == "sse":
        asyncio.run(print_registered_tools(mcp))
        url = f"http://localhost:{args.port}"
        print(f"[MCP] Launching FastAPI SSE server at {url}")

        # import webbrowser
        # webbrowser.open_new_tab(url)

        app = build_mcp_fastapi_app(mcp._mcp_server, debug=True)
        uvicorn.run(app, host=args.host, port=args.port)
    elif args.mode == "http":
        mcp.run(transport="streamable-http")
    else:
        print("[Portfolio MCP] Running in stdio (CLI) mode...")
        mcp.run()

if __name__ == "__main__":
    main()
