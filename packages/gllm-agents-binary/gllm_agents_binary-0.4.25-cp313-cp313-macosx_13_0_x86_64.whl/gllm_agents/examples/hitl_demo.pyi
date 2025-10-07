import asyncio
import httpx
from _typeshed import Incomplete
from dataclasses import dataclass
from gllm_agents.schema.hitl import ApprovalRequest as ApprovalRequest
from gllm_agents.utils.env_loader import load_local_env as load_local_env
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from langchain_core.tools import tool
from starlette.applications import Starlette
from starlette.requests import Request as Request

logger_manager: Incomplete
logger: Incomplete

@tool
def check_candidate_inbox(candidate_email: str) -> str:
    """Retrieve the latest email from a candidate (safe tool)."""
@tool
def validate_candidate(candidate_name: str, role: str, score: int) -> str:
    """Record the candidate decision in the applicant tracking system."""
@tool
def send_candidate_email(candidate_email: str, subject: str, body: str) -> str:
    """Send an email update to the candidate."""

CANDIDATE_PROFILES: dict[str, dict[str, str | int | bool]]
CANDIDATE_SEQUENCE: list[dict[str, str | int | bool]]
NAME_INDEX: Incomplete

class _ServerContext:
    def __init__(self, app: Starlette, host: str, port: int) -> None: ...
    async def __aenter__(self) -> _ServerContext: ...
    async def __aexit__(self, exc_type, exc, tb) -> None: ...

@dataclass
class RunContext:
    """Context object containing runtime dependencies for the HITL demo server."""
    http_client: httpx.AsyncClient
    host: str
    port: int
    pending_queue: asyncio.Queue[ApprovalRequest]

async def main() -> None:
    """Interactive HITL approval demo."""
