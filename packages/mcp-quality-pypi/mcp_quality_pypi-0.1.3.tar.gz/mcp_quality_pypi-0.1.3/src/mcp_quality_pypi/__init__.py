from mcp.server.fastmcp import FastMCP
import service.business.quality as quality

# Create an MCP server
mcp = FastMCP("Demo")

# Create an MCP servermcp = FastMCP("Demo")# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

def main() -> None:
    mcp.run(transport='stdio')
