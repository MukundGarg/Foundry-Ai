"""
Foundry AI — Agent Registry
Maps agent type names to their implementation classes.
"""

from agents.database_agent import DatabaseAgent
from agents.backend_agent import BackendAgent
from agents.frontend_agent import FrontendAgent
from agents.devops_agent import DevOpsAgent
from agents.integration_agent import IntegrationAgent


AGENT_REGISTRY = {
    "DatabaseAgent": DatabaseAgent,
    "BackendAgent": BackendAgent,
    "FrontendAgent": FrontendAgent,
    "DevOpsAgent": DevOpsAgent,
    "IntegrationAgent": IntegrationAgent,
}


def get_agent(agent_type: str, project_id: str):
    """Get an agent instance by type name."""
    agent_class = AGENT_REGISTRY.get(agent_type)
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}. Available: {list(AGENT_REGISTRY.keys())}")
    return agent_class(project_id)


def list_agents():
    """List all available agent types."""
    return [
        {
            "type": name,
            "description": cls.description,
        }
        for name, cls in AGENT_REGISTRY.items()
    ]
