from _typeshed import Incomplete
from gllm_agents.agent import LangGraphAgent as LangGraphAgent
from gllm_agents.utils.env_loader import load_local_env as load_local_env
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager

logger: Incomplete
SERVER_AGENT_NAME: str

def main(host: str, port: int):
    """Runs the Mem0 Memory-enabled Coordinator A2A server."""
