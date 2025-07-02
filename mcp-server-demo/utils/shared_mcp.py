from mcp.server.fastmcp import FastMCP

# # Singleton instance
# _mcp_instance = FastMCP("PortfolioMCP")

# def get_mcp():
#     global _mcp_instance
#     if _mcp_instance is None:
#         _mcp_instance = FastMCP("PortfolioMCP")
#     return _mcp_instance

mcp = FastMCP("PortfolioMCP")
def set_mcp(mcp_instance: FastMCP):
    global mcp
    mcp = mcp_instance
    return mcp

class Session:
    login_cert = None

work_cache = {}
