from fastapi import FastAPI, Request
from starlette.responses import Response
from mcp.server import Server
from mcp.server.sse import SseServerTransport

def build_mcp_fastapi_app(mcp_server: Server, *, debug: bool = False) -> FastAPI:
    """Reusable FastAPI app builder for any MCP server."""
    sse = SseServerTransport("/messages/")
    app = FastAPI(
        debug=debug,
        title="MCP Tool Server",
        version="1.0",
    )

    @app.get("/sse")
    async def handle_sse(request: Request) -> Response:
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options()
            )

    app.mount("/messages", sse.handle_post_message)

    @app.get("/")
    def health_check():
        return {"status": "MCP Server Ready 🟢"}

    return app
