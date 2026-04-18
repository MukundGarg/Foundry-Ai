"""
Specialized agent implementations.
Each agent type tunes temperature and token limits for its domain.
"""

from agents.base_agent import BaseAgent


class ResearcherAgent(BaseAgent):
    agent_type = "researcher"

    def _get_temperature(self) -> float:
        return 0.3  # More factual, less creative

    def _get_max_tokens(self) -> int:
        return 4096


class CoderAgent(BaseAgent):
    agent_type = "coder"

    def _get_temperature(self) -> float:
        return 0.2  # Deterministic code output

    def _get_max_tokens(self) -> int:
        return 4096


class AnalystAgent(BaseAgent):
    agent_type = "analyst"

    def _get_temperature(self) -> float:
        return 0.4

    def _get_max_tokens(self) -> int:
        return 4096


class DesignerAgent(BaseAgent):
    agent_type = "designer"

    def _get_temperature(self) -> float:
        return 0.7  # More creative

    def _get_max_tokens(self) -> int:
        return 3000


class WriterAgent(BaseAgent):
    agent_type = "writer"

    def _get_temperature(self) -> float:
        return 0.8

    def _get_max_tokens(self) -> int:
        return 4096


class TesterAgent(BaseAgent):
    agent_type = "tester"

    def _get_temperature(self) -> float:
        return 0.2

    def _get_max_tokens(self) -> int:
        return 3000


class IntegratorAgent(BaseAgent):
    agent_type = "integrator"

    def _get_temperature(self) -> float:
        return 0.5

    def _get_max_tokens(self) -> int:
        return 4096
