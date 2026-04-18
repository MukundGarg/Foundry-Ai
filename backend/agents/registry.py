"""
Agent registry — maps agent_type strings to agent classes.
"""

from services.base import BaseAIService
from agents.base_agent import BaseAgent
from agents.specialized import (
    ResearcherAgent,
    CoderAgent,
    AnalystAgent,
    DesignerAgent,
    WriterAgent,
    TesterAgent,
    IntegratorAgent,
)

AGENT_REGISTRY: dict[str, type[BaseAgent]] = {
    "researcher": ResearcherAgent,
    "coder": CoderAgent,
    "analyst": AnalystAgent,
    "designer": DesignerAgent,
    "writer": WriterAgent,
    "tester": TesterAgent,
    "integrator": IntegratorAgent,
}


def get_agent(agent_type: str, service: BaseAIService) -> BaseAgent:
    """Instantiate the correct agent for the given type."""
    agent_class = AGENT_REGISTRY.get(agent_type, BaseAgent)
    return agent_class(service)
