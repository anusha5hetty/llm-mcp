from mcp.server.fastmcp import FastMCP

# Singleton instance
_mcp_instance = None

def get_mcp():
    global _mcp_instance
    if _mcp_instance is None:
        _mcp_instance = FastMCP("PortfolioMCP")
    return _mcp_instance

# Shortcut for convenience
mcp = get_mcp()
