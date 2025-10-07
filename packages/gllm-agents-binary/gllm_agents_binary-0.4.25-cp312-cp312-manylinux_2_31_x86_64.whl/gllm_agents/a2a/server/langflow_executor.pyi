from _typeshed import Incomplete
from a2a.server.agent_execution import RequestContext as RequestContext
from a2a.server.events.event_queue import EventQueue as EventQueue
from a2a.server.tasks import TaskUpdater as TaskUpdater
from abc import ABC
from gllm_agents.a2a.server.base_executor import BaseA2AExecutor as BaseA2AExecutor, StatusUpdateParams as StatusUpdateParams
from gllm_agents.agent.langflow_agent import LangflowAgent as LangflowAgent
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager

logger: Incomplete

class LangflowA2AExecutor(BaseA2AExecutor, ABC):
    """A2A executor for Langflow agents.

    This class extends BaseA2AExecutor to provide A2A execution capabilities
    for Langflow agents. It follows the same patterns as LangGraphA2AExecutor
    but handles Langflow-specific streaming and execution logic.

    Attributes:
        agent: The LangflowAgent instance to be executed.
    """
    agent: LangflowAgent
    def __init__(self, langflow_agent_instance: LangflowAgent) -> None:
        """Initialize the LangflowA2AExecutor.

        Args:
            langflow_agent_instance: A fully initialized instance of LangflowAgent.

        Raises:
            TypeError: If langflow_agent_instance is not an instance of LangflowAgent.
        """
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Process an incoming agent request using a Langflow agent.

        This method handles the execution lifecycle for Langflow agents:
        1. Performs initial validation and setup
        2. Creates agent processing coroutine
        3. Manages the execution lifecycle through BaseA2AExecutor

        Args:
            context: The A2A request context containing message details,
                task ID, and context ID.
            event_queue: The queue for sending A2A events back to the server.
        """
