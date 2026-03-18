import logging
import sys

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Configure logging to stderr so it doesn't interfere with STDIO transport
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)

mcp = FastMCP(
    "actual-budget",
    instructions="MCP server for Actual Budget — manage accounts, transactions, budgets, and categories",
)

# Import tool modules to register them with the MCP server
import server.tools.accounts  # noqa: E402, F401
import server.tools.budgets  # noqa: E402, F401
import server.tools.categories  # noqa: E402, F401
import server.tools.transactions  # noqa: E402, F401


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
