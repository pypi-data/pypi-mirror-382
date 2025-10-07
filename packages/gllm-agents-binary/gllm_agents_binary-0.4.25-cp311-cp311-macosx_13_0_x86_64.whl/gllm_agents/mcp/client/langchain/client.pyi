from _typeshed import Incomplete
from gllm_agents.mcp.client.base_mcp_client import BaseMCPClient as BaseMCPClient
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from gllm_tools.mcp.client.config import MCPConfiguration as MCPConfiguration
from gllm_tools.mcp.client.resource import MCPResource as MCPResource
from gllm_tools.mcp.client.tool import MCPTool as MCPTool
from langchain_core.tools import StructuredTool
from mcp.types import CallToolResult as CallToolResult, EmbeddedResource, ImageContent
from pydantic import AnyUrl as AnyUrl

NonTextContent = ImageContent | EmbeddedResource
logger: Incomplete

class LangchainMCPClient(BaseMCPClient):
    """Langchain MCP Client with Session Persistence.

    This client extends BaseMCPClient to provide LangChain-specific tool conversion
    while maintaining persistent MCP sessions and connection reuse across tool calls.
    """
    RESOURCE_FETCH_TIMEOUT: int
    def __init__(self, servers: dict[str, MCPConfiguration]) -> None:
        """Initialize LangChain MCP client.

        Args:
            servers (dict[str, MCPConfiguration]): Dictionary of MCP server configurations
        """
    async def initialize(self) -> None:
        """Initialize all sessions for LangChain client.

        This method initializes the base MCP sessions and prepares for tool caching.

        Raises:
            Exception: If base initialization fails
        """
    async def get_tools(self, server: str | None = None) -> list[StructuredTool]:
        """Get LangChain StructuredTools with smart caching.

        Converts MCP tools to LangChain format and caches them for better performance
        on repeated access. Cache is keyed by server parameter.

        Args:
            server (str | None): Optional server name to filter tools. If None, returns all tools.

        Returns:
            list[StructuredTool]: List of cached LangChain StructuredTool instances
        """
    async def cleanup(self) -> None:
        """Cleanup LangChain MCP resources.

        This method extends base class cleanup and clears the LangChain tool cache.
        """
