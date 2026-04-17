"""
Foundry AI — WebSocket Router
Real-time progress updates for project pipeline execution.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ws_manager import manager
import structlog

logger = structlog.get_logger()

router = APIRouter()


@router.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """
    WebSocket endpoint for real-time project updates.
    
    Events emitted:
    - council_started: Council begins analyzing idea
    - council_analysis: Individual model analysis complete
    - council_prd: PRD generated
    - council_architecture: Architecture plan ready
    - council_agent_plan: Agent task plan created
    - agent_started: An agent begins execution
    - agent_progress: Agent progress update
    - agent_completed: Agent task finished
    - agent_failed: Agent task failed
    - review_started: Council review begins
    - integration_started: Integration engine running
    - project_completed: Final MVP ready
    - project_failed: Pipeline failed
    - log: General log message
    """
    await manager.connect(websocket, project_id)
    logger.info("ws_connected", project_id=project_id)

    try:
        while True:
            # Keep connection alive, receive any client messages
            data = await websocket.receive_text()
            # Client can send ping/pong or commands
            if data == "ping":
                await websocket.send_json({"event": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)
        logger.info("ws_disconnected", project_id=project_id)
