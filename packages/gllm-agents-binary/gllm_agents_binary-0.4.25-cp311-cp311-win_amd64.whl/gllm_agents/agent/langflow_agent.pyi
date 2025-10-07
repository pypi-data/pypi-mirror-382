from _typeshed import Incomplete
from a2a.types import AgentCard as AgentCard
from gllm_agents.agent.base_agent import BaseAgent as BaseAgent
from gllm_agents.clients.langflow import LangflowApiClient as LangflowApiClient
from gllm_agents.clients.langflow.types import LangflowEventType as LangflowEventType
from gllm_agents.schema.agent import LangflowAgentConfig as LangflowAgentConfig
from gllm_agents.types import A2AEvent as A2AEvent, A2AStreamEventType as A2AStreamEventType
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from typing import Any, AsyncGenerator

logger: Incomplete

class LangflowAgent(BaseAgent):
    """Langflow agent implementation for executing Langflow flows.

    This agent integrates with Langflow APIs to execute flows while providing
    full compatibility with the SDK's agent framework, including:
    - Synchronous and asynchronous execution
    - Regular and A2A streaming support
    - Session management for conversation continuity
    - Error handling and retry logic
    - Credential management through BaseAgent

    The agent inherits from BaseAgent to leverage existing A2A infrastructure
    while implementing Langflow-specific execution logic.
    """
    langflow_config: Incomplete
    flow_id: Incomplete
    api_client: Incomplete
    def __init__(self, name: str, flow_id: str, description: str | None = None, base_url: str | None = None, api_key: str | None = None, config: LangflowAgentConfig | dict[str, Any] | None = None, **kwargs: Any) -> None:
        """Initialize the LangflowAgent.

        Args:
            name: The name of the agent.
            flow_id: The unique identifier of the Langflow flow to execute.
            description: Human-readable description.
            base_url: The base URL of the Langflow API server.
            api_key: The API key for Langflow authentication.
            config: Langflow-specific configuration or dict.
            **kwargs: Additional keyword arguments passed to BaseAgent.
        """
    def run(self, query: str, **kwargs: Any) -> dict[str, Any]:
        """Synchronously run the Langflow agent.

        Args:
            query: The input query for the agent.
            **kwargs: Additional keyword arguments.

        Returns:
            Dictionary containing the agent's response.
        """
    async def arun(self, query: str, **kwargs: Any) -> dict[str, Any]:
        """Asynchronously run the Langflow agent.

        Args:
            query: The input query for the agent.
            **kwargs: Additional keyword arguments.

        Returns:
            Dictionary containing the agent's response and metadata.
        """
    async def arun_stream(self, query: str, **kwargs: Any) -> AsyncGenerator[str | dict[str, Any], None]:
        """Asynchronously stream the Langflow agent's response.

        Args:
            query: The input query for the agent.
            **kwargs: Additional keyword arguments.

        Yields:
            Chunks of output (strings or dicts) from the streaming response.
        """
    async def arun_a2a_stream(self, query: str, **kwargs: Any) -> AsyncGenerator[dict[str, Any], None]:
        """Asynchronously stream the agent's response in A2A format.

        This method converts Langflow streaming events into A2A-compatible events
        following the patterns established by BaseLangGraphAgent.

        Args:
            query: The input query for the agent.
            **kwargs: Additional keyword arguments.

        Yields:
            A2A-compatible event dictionaries with semantic event types.
        """
    def register_a2a_agents(self, agents: list[AgentCard]) -> None:
        """Register A2A agents (not supported for Langflow agents).

        Args:
            agents: List of AgentCard instances.

        Raises:
            NotImplementedError: Langflow agents don't support A2A agent registration.
        """
    def add_mcp_server(self, mcp_config: dict[str, dict[str, Any]]) -> None:
        """Add MCP server configuration (not supported for Langflow agents).

        Args:
            mcp_config: MCP server configuration.

        Raises:
            NotImplementedError: Langflow agents don't support MCP servers.
        """
    async def health_check(self) -> bool:
        """Check if the Langflow API is accessible.

        Returns:
            True if the API is accessible, False otherwise.
        """
