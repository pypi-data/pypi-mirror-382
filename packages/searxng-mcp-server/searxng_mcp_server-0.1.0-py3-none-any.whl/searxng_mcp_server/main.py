import sys

from fastmcp import FastMCP
from fastmcp.tools.tool import Tool

from .config import Config, create_argument_parser
from .log import get_logger
from .tools import SearxNGClient

logger = get_logger(__name__)

# Initialize FastMCP server
mcp = FastMCP("SearxNG Search Server")


def main() -> None:
    """Main entry point for the MCP server."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Create configuration
    try:
        config = Config.from_env(args)
        logger.info("initialized with searxng_url: %s", config.searxng_url)
    except Exception as e:
        logger.error("failed to create configuration: %s", e)
        sys.exit(1)

    # Initialize client
    try:
        client = SearxNGClient(config)
    except Exception as e:
        logger.error("failed to initialize client: %s", e)
        sys.exit(1)

    # Register tools with MCP server
    mcp.add_tool(Tool.from_function(client.search_web))
    mcp.add_tool(Tool.from_function(client.search_images))
    mcp.add_tool(Tool.from_function(client.search_videos))
    mcp.add_tool(Tool.from_function(client.search_news))

    # Run the MCP server
    try:
        logger.info("starting SearxNG MCP server")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("server stopped by user")
    except Exception as e:
        logger.error("server failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
