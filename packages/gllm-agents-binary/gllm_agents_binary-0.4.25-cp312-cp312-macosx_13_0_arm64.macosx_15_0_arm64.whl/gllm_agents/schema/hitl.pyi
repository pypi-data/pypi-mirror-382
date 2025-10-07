from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

__all__ = ['ApprovalDecisionType', 'ApprovalRequest', 'ApprovalDecision', 'ApprovalLogEntry']

class ApprovalDecisionType(StrEnum):
    """Enumeration of possible approval decision types."""
    APPROVED = 'approved'
    REJECTED = 'rejected'
    SKIPPED = 'skipped'
    TIMEOUT_SKIP = 'timeout_skip'
    PENDING = 'pending'

@dataclass
class ApprovalRequest:
    """Represents an in-flight prompt shown to the operator."""
    request_id: str
    tool_name: str
    arguments_preview: str
    context: dict[str, str] | None = ...
    created_at: datetime | None = ...
    timeout_at: datetime | None = ...
    def __post_init__(self) -> None:
        """Initialize timestamps if not provided."""
    @classmethod
    def create(cls, tool_name: str, arguments_preview: str, context: dict[str, str] | None = None) -> ApprovalRequest:
        """Create a new approval request with generated request_id."""

@dataclass
class ApprovalDecision:
    """Captures the operator outcome."""
    request_id: str
    decision: ApprovalDecisionType
    operator_input: str
    decided_at: datetime | None = ...
    latency_ms: int | None = ...
    def __post_init__(self) -> None:
        """Initialize timestamp if not provided."""

@dataclass
class ApprovalLogEntry:
    """Structured log entry for HITL decisions."""
    request_id: str
    tool_name: str
    decision: str
    event: str = ...
    agent_id: str | None = ...
    thread_id: str | None = ...
    additional_context: dict[str, Any] | None = ...
    timestamp: datetime | None = ...
    def __post_init__(self) -> None:
        """Initialize timestamp if not provided."""
