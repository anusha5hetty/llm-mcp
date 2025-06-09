import os
import argparse
import importlib
import uvicorn
import asyncio
from utils.fastapi_factory import build_mcp_fastapi_app

def load_tool_module(module_name: str):
    """Dynamically import and return the tool module."""
    return importlib.import_module(f"tools.{module_name}")

async def print_registered_tools(mcp):
    tools = await mcp.list_tools()
    print("[MCP] Available tools:")
    for t in tools:
        print("-", t.name)

def main():
    parser = argparse.ArgumentParser(description="Run any MCP tool server")
    parser.add_argument("--tool", required=True, help="Tool module name (without .py)")
    parser.add_argument("--mode", choices=["sse", "stdio"], default=os.getenv("MCP_MODE", "sse"))
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    # Step 1: Load the tool module
    try:
        tool_module = load_tool_module(args.tool)
        mcp = tool_module.mcp
    except Exception as e:
        print(f"❌ Failed to load tool '{args.tool}': {e}")
        return

    # Step 2: Run based on mode
    if args.mode == "sse":
        asyncio.run(print_registered_tools(mcp))
        url = f"http://localhost:{args.port}"
        print(f"[MCP] Launching FastAPI SSE server at {url}")

        import webbrowser
        webbrowser.open_new_tab(url)

        app = build_mcp_fastapi_app(mcp._mcp_server, debug=True)
        uvicorn.run(app, host=args.host, port=args.port)
    else:
        print("[MCP] Running in stdio (CLI) mode...")
        mcp.run()

if __name__ == "__main__":
    main()
