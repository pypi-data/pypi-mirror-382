import abc
from abc import ABC, abstractmethod
from gllm_agents.agent.hitl.manager import ApprovalManager as ApprovalManager
from gllm_agents.schema.hitl import ApprovalDecision as ApprovalDecision, ApprovalRequest as ApprovalRequest

class BasePromptHandler(ABC, metaclass=abc.ABCMeta):
    """Abstract base class for prompt handlers used in HITL flows."""
    def attach_manager(self, manager: ApprovalManager) -> None:
        """Optionally attach the ``ApprovalManager`` coordinating approvals."""
    @abstractmethod
    async def prompt_for_decision(self, request: ApprovalRequest, timeout_seconds: int, context_keys: list[str] | None = None) -> ApprovalDecision:
        """Collect and return a decision for the given approval request."""
