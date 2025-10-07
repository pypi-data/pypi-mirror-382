from gllm_agents.agent.langflow_agent import LangflowAgent as LangflowAgent
from gllm_agents.clients.langflow import LangflowApiClient as LangflowApiClient

async def fetch_flow_id() -> tuple[str, str]:
    """Fetch available flows and return the first flow ID and name."""
async def create_agent(flow_id: str, flow_name: str) -> LangflowAgent:
    """Create and configure the Langflow agent."""
async def demonstrate_regular_execution(agent: LangflowAgent) -> None:
    """Demonstrate regular execution."""
async def demonstrate_streaming(agent: LangflowAgent) -> None:
    """Demonstrate streaming execution."""
async def demonstrate_session_management(agent: LangflowAgent) -> None:
    """Demonstrate session management."""
async def main() -> None:
    """Demonstrate basic Langflow agent usage."""
