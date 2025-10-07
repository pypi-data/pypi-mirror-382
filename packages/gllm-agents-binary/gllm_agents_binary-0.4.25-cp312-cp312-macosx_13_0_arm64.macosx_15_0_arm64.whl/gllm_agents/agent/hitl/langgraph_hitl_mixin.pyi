from _typeshed import Incomplete
from gllm_agents.agent.hitl.config import ToolApprovalConfig as ToolApprovalConfig
from gllm_agents.agent.hitl.manager import ApprovalManager as ApprovalManager
from gllm_agents.schema.hitl import ApprovalDecision as ApprovalDecision, ApprovalDecisionType as ApprovalDecisionType, ApprovalRequest as ApprovalRequest
from gllm_agents.schema.langgraph import ToolCallResult as ToolCallResult
from gllm_agents.tools.tool_config_injector import TOOL_CONFIGS_KEY as TOOL_CONFIGS_KEY
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from langgraph.types import StreamWriter as StreamWriter
from typing import Any, Callable

logger: Incomplete
MAX_CONTEXT_MESSAGE_LENGTH: int

class LangGraphHitLMixin:
    """Provide Human-in-the-Loop helpers for LangGraph agents."""
    tool_configs: dict[str, Any] | None
    name: str
    @property
    def hitl_manager(self) -> ApprovalManager | None:
        """Return the active ``ApprovalManager``, creating one if needed."""
    @hitl_manager.setter
    def hitl_manager(self, manager: ApprovalManager | None) -> None: ...
    def ensure_hitl_manager(self) -> ApprovalManager | None:
        """Ensure an ``ApprovalManager`` exists when HITL configs are present."""
    def use_hitl_manager(self, manager: ApprovalManager) -> None:
        """Replace the current ``ApprovalManager`` with the supplied instance."""
    def register_hitl_notifier(self, notifier: Callable[[ApprovalRequest], None]) -> None:
        """Register a notifier callback to receive HITL approval requests."""
