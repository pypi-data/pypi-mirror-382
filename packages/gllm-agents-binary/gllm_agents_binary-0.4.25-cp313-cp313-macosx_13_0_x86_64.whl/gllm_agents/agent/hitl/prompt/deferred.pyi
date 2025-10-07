from gllm_agents.agent.hitl.manager import ApprovalManager as ApprovalManager
from gllm_agents.agent.hitl.prompt.base import BasePromptHandler as BasePromptHandler
from gllm_agents.schema.hitl import ApprovalDecision as ApprovalDecision, ApprovalDecisionType as ApprovalDecisionType, ApprovalRequest as ApprovalRequest
from typing import Callable

class DeferredPromptHandler(BasePromptHandler):
    """Prompt handler that defers tool execution until an external decision is received."""
    def __init__(self, notify: Callable[[ApprovalRequest], None] | None = None) -> None:
        """Initialize the deferred prompt handler."""
    def attach_manager(self, manager: ApprovalManager) -> None:
        """Attach the ``ApprovalManager`` orchestrating approvals."""
    async def prompt_for_decision(self, request: ApprovalRequest, timeout_seconds: int, context_keys: list[str] | None = None) -> ApprovalDecision:
        """Register a waiter and return a pending decision sentinel."""
