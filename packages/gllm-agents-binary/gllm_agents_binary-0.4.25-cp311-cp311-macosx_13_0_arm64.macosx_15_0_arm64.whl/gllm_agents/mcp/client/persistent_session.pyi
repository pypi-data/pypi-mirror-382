from _typeshed import Incomplete
from gllm_agents.mcp.client.connection_manager import MCPConnectionManager as MCPConnectionManager
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from gllm_tools.mcp.client.config import MCPConfiguration as MCPConfiguration
from mcp import ClientSession
from mcp.types import CallToolResult as CallToolResult, Tool as Tool
from typing import Any

logger: Incomplete

class PersistentMCPSession:
    """Persistent MCP session that reuses connections.

    This session wrapper manages the connection lifecycle and caches tools
    to avoid repeated initialization overhead. It provides automatic reconnection
    and thread-safe operations.
    """
    server_name: Incomplete
    config: Incomplete
    connection_manager: Incomplete
    client_session: ClientSession | None
    tools: list[Tool]
    def __init__(self, server_name: str, config: MCPConfiguration) -> None:
        """Initialize persistent session.

        Args:
            server_name: Name of the MCP server
            config: MCP server configuration
        """
    async def initialize(self) -> None:
        """Initialize session once and cache tools.

        This method is idempotent and can be called multiple times safely.

        Raises:
            Exception: If session initialization fails
        """
    async def call_tool(self, name: str, arguments: dict[str, Any]) -> CallToolResult:
        """Call MCP tool using persistent session.

        Args:
            name (str): Tool name
            arguments (dict[str, Any]): Tool arguments

        Returns:
            CallToolResult: Tool call result

        Raises:
            Exception: If tool call fails
        """
    async def read_resource(self, uri: str) -> Any:
        """Read an MCP resource using persistent session.

        Args:
            uri (str): The URI of the resource to read

        Returns:
            Any: The resource content

        Raises:
            Exception: If resource reading fails
        """
    async def list_tools(self) -> list[Tool]:
        """Get cached tools list.

        Returns:
            list[Tool]: List of available tools
        """
    def get_tools_count(self) -> int:
        """Get count of cached tools without expensive copying.

        Returns:
            Count of available tools
        """
    async def ensure_connected(self) -> None:
        """Ensure connection is healthy, reconnect if needed.

        This method provides automatic reconnection capability.

        Raises:
            Exception: If reconnection fails
        """
    async def disconnect(self) -> None:
        """Disconnect session gracefully.

        This method cleans up all resources and connections.
        """
    @property
    def is_initialized(self) -> bool:
        """Check if session is initialized.

        Returns:
            bool: True if initialized and connected, False otherwise
        """
