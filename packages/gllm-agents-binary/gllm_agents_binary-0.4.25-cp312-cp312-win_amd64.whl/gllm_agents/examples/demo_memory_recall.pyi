from _typeshed import Incomplete
from datetime import datetime
from gllm_agents.agent import LangGraphAgent as LangGraphAgent
from langchain_core.messages import HumanMessage as HumanMessage

class MemoryTestResult:
    """Container for test scenario results."""
    JUDGE_SUCCESS_THRESHOLD: float
    MEMORY_DISPLAY_LIMIT: int
    scenario_name: Incomplete
    query: Incomplete
    response: Incomplete
    memory_fetched: Incomplete
    error: Incomplete
    success: Incomplete
    judge_verdict: Incomplete
    judge_score: Incomplete
    def __init__(self, scenario_name: str, query: str, response: str = None, memory_fetched: str = None, error: str = None) -> None:
        """Initialize a memory test result.

        Args:
            scenario_name: Name of the test scenario.
            query: The input query for the scenario.
            response: The agent's response (optional).
            memory_fetched: The raw memory retrieved from the tool (optional).
            error: Any error message (optional).
        """
    def set_success_from_judge(self, verdict: str, score: float | None):
        '''Set success using judge verdict and confidence score.

        Success criteria: (verdict == "grounded" or verdict == "general_knowledge") and
        score >= JUDGE_SUCCESS_THRESHOLD.
        '''

def print_test_summary(results: list[MemoryTestResult], start_time: datetime):
    """Print a clean summary of all test results."""
async def evaluate_with_judge(judge_agent: LangGraphAgent, query: str, response: str, memory_fetched: str = None) -> tuple[str | None, float | None]:
    """Evaluate if the response is grounded in memory using the judge agent."""
async def run_all_scenarios() -> None:
    """Run all memory recall test scenarios with a single reused agent and show clean summary."""
