from _typeshed import Incomplete
from collections.abc import Callable as Callable
from gllm_agents.memory.constants import MemoryDefaults as MemoryDefaults
from gllm_agents.memory.mem0_memory import Mem0Memory as Mem0Memory
from gllm_agents.utils.datetime import is_valid_date_string as is_valid_date_string, next_day_iso as next_day_iso
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from langchain_core.runnables import RunnableConfig as RunnableConfig
from langchain_core.tools import BaseTool
from pydantic import BaseModel
from typing import Any, ClassVar

logger: Incomplete
MEMORY_SEARCH_TOOL_NAME: str

class MemoryConfig(BaseModel):
    """Tool configuration schema for memory operations."""
    user_id: str

class Mem0SearchInput(BaseModel):
    """Input schema for Mem0 unified retrieval tool.

    Supports both semantic search (with query) and pure date-based recall (without query).
    Time periods are specified only via explicit dates (start_date/end_date in YYYY-MM-DD).
    """
    query: str | None
    start_date: str | None
    end_date: str | None
    limit: int | None
    categories: list[str] | None
    metadata: dict[str, Any] | None

class Mem0SearchTool(BaseTool):
    """LangChain tool for unified Mem0 memory retrieval with flexible time filtering.

    Supports both semantic search (with query) and pure date-based recall (without query).
    Uses RunnableConfig for user_id configuration instead of ContextVar.
    """
    name: str
    description: str
    args_schema: type[Mem0SearchInput]
    tool_config_schema: type[BaseModel]
    memory: Mem0Memory
    default_user_id: str | None
    user_id_provider: Callable[[], str | None] | None
    MINIMUM_MEMORY_RETRIEVAL: ClassVar[int]
    def __init__(self, memory: Mem0Memory, *, default_user_id: str | None = None, user_id_provider: Callable[[], str | None] | None = None, **kwargs: Any) -> None:
        """Initialize the Mem0 search tool for the provided memory backend."""
    def format_hits(self, hits: list[dict[str, Any]], with_tag: bool = False) -> str:
        """Format hits into a string with optional tags.

        Args:
            hits: List of memory hits to format.
            with_tag: Whether to include tags in the formatted output.

        Returns:
            str: Formatted string of hits.
        """
