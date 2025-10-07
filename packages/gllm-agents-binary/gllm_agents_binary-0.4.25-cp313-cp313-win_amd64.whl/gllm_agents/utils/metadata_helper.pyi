from _typeshed import Incomplete
from enum import StrEnum
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from gllm_agents.utils.token_usage_helper import STEP_USAGE_KEY as STEP_USAGE_KEY, TOTAL_USAGE_KEY as TOTAL_USAGE_KEY
from typing import Any

logger: Incomplete

def start_step_counter_scope(start: int = 1) -> None:
    """Begin a step counter scope, resetting only when entering the outermost scope.

    Args:
        start: Starting step number for the counter. Defaults to 1.
    """
def end_step_counter_scope() -> None:
    """Exit a step counter scope, maintaining parent scope counters.

    Decrements the depth counter while preserving the step count for parent scopes.
    """
def get_next_step_number() -> int:
    """Return the next step number within the active scope.

    Returns:
        int: The next sequential step number in the current scope.
    """

THINKING_DATA_TYPE: str
FINAL_AGENT_THINKING_FINISHED_CONTENT: str
FINAL_THINKING_AND_ACTIVITY_INFO: Incomplete
DEFAULT_THINKING_AND_ACTIVITY_INFO: Incomplete
TOOL_EXECUTION_RUNNING_TEMPLATE: str
TOOL_EXECUTION_COMPLETE_TEMPLATE: str
SUBAGENT_DELEGATION_TEMPLATE: str
SUBAGENT_COMPLETE_TEMPLATE: str
MIXED_EXECUTION_TEMPLATE: str
DELEGATE_PREFIX: str

class DefaultStepMessages(StrEnum):
    """Constants for default step indicator messages."""
    EN = 'Performing agent tasks'
    ID = 'Melakukan tugas agen'

class Kind(StrEnum):
    """Constants for metadata kind values."""
    AGENT_STEP = 'agent_step'
    AGENT_THINKING_STEP = 'agent_thinking_step'
    FINAL_RESPONSE = 'final_response'
    FINAL_THINKING_STEP = 'final_agent_thinking_step'
    AGENT_DEFAULT = 'agent_default'
    TOKEN = 'token'

class Status(StrEnum):
    """Constants for metadata status values."""
    RUNNING = 'running'
    FINISHED = 'finished'
    STOPPED = 'stopped'

class MetadataFieldKeys(StrEnum):
    """Enumeration of standard metadata field keys used in A2A events."""
    KIND = 'kind'
    STATUS = 'status'
    TIME = 'time'
    MESSAGE = 'message'
    TOOL_INFO = 'tool_info'
    REFERENCES = 'references'
    THINKING_AND_ACTIVITY_INFO = 'thinking_and_activity_info'
    STEP_USAGE = STEP_USAGE_KEY
    TOTAL_USAGE = TOTAL_USAGE_KEY
    STREAMING = 'streaming'

class MetadataTimeTracker:
    """Tracks cumulative execution time across agent steps for final response metadata.

    This class provides a clean way to accumulate execution times from individual
    agent steps and apply the total time to final response metadata.

    Attributes:
        FLOAT_EPSILON: Epsilon value for floating point comparisons to avoid precision issues.
    """
    FLOAT_EPSILON: float
    def __init__(self) -> None:
        """Initialize the time tracker with zero accumulated time."""
    def update_response_metadata(self, response: dict[str, Any]) -> dict[str, Any]:
        """Update response metadata with accumulated time tracking.

        Args:
            response: Response dictionary containing metadata to update.

        Returns:
            dict[str, Any]: Response with updated metadata for final responses. If any error occurs,
                returns the original response unchanged.
        """

def create_metadata(content: str = '', status: Status = ..., is_final: bool = False, existing_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create metadata for A2A responses with content-based message.

    Args:
        content: The content to create metadata for.
        status: The status of the content.
        is_final: Whether the content is final.
        existing_metadata: Optional existing metadata to merge with. Existing metadata
            takes precedence over generated metadata for conflicting keys.

    Returns:
        dict[str, Any]: The metadata for the content, merged with existing metadata if provided.
    """
def create_tool_processing_metadata(original_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create metadata for tool processing events (tool_call and tool_result).

    Args:
        original_metadata: Optional original metadata to merge with.

    Returns:
        dict[str, Any]: Metadata dictionary with agent_thinking_step kind and no message/time/status.
    """
def create_status_update_metadata(content: str, custom_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create metadata for status update events with content-based rules.

    Args:
        content: The content of the status update.
        custom_metadata: Optional custom metadata to merge with.

    Returns:
        dict[str, Any]: Metadata dictionary following the specific rules for different content types.
    """
