from _typeshed import Incomplete
from gllm_agents.agent.langflow_agent import LangflowAgent as LangflowAgent
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager

logger: Incomplete
SERVER_AGENT_NAME: str

def main(host: str, port: int):
    """Runs the Langflow A2A server."""
