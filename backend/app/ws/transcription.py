"""WebSocket endpoint for audio streaming, transcription, and RAG insights."""

import contextlib
import uuid

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.security import decode_access_token
from app.database import async_session
from app.models.insight import Insight, InsightType
from app.models.transcription import Transcription
from app.services.deepgram import DeepgramSession
from app.services.meeting_manager import meeting_manager
from app.services.rag import add_transcription_and_maybe_generate, clear_buffer

logger = structlog.get_logger()

router = APIRouter()

# Active Deepgram sessions per meeting
_deepgram_sessions: dict[uuid.UUID, DeepgramSession] = {}

# Meeting → project_id mapping (set when WS connects)
_meeting_projects: dict[uuid.UUID, uuid.UUID] = {}


@router.websocket("/ws/meeting/{meeting_id}")
async def meeting_websocket(
    websocket: WebSocket,
    meeting_id: uuid.UUID,
    token: str = "",
    project_id: str = "",
) -> None:
    """WebSocket endpoint for a meeting session.

    Query params:
      token — JWT token for authentication
      project_id — required to enable RAG context search
    """
    # Authenticate via JWT query param
    if not token:
        await websocket.accept()
        await websocket.close(code=4001, reason="Missing token")
        return
    payload = decode_access_token(token)
    if payload is None:
        await websocket.accept()
        await websocket.close(code=4001, reason="Invalid token")
        return

    # Parse project_id safely
    parsed_project_id: uuid.UUID | None = None
    if project_id:
        with contextlib.suppress(ValueError):
            parsed_project_id = uuid.UUID(project_id)

    # Extract user role from JWT for role-aware pipeline
    user_role = payload.get("role", "developer")

    await meeting_manager.connect(meeting_id, websocket, role=user_role)

    if parsed_project_id:
        _meeting_projects[meeting_id] = parsed_project_id

    # Start Deepgram session if not already running
    if meeting_id not in _deepgram_sessions:

        async def on_transcription(msg: dict) -> None:
            """Broadcast transcription + trigger RAG pipeline."""
            await meeting_manager.broadcast(meeting_id, msg)

            # Feed transcription to RAG pipeline
            payload = msg.get("payload", {})
            text = payload.get("text", "")
            is_final = payload.get("is_final", False)
            pid = _meeting_projects.get(meeting_id)

            if text:
                async with async_session() as db:
                    # Persist transcription segment
                    if is_final:
                        db.add(Transcription(
                            meeting_id=meeting_id,
                            speaker=payload.get("speaker", "Speaker"),
                            text=text,
                            is_final=True,
                        ))
                        await db.commit()

                    # Feed to RAG pipeline
                    if pid:
                        roles = meeting_manager.get_connected_roles(
                            meeting_id
                        )
                        result = await add_transcription_and_maybe_generate(
                            db, meeting_id, pid, text, is_final,
                            connected_roles=roles,
                        )
                        if result:
                            insight_list = (
                                result
                                if isinstance(result, list)
                                else [result]
                            )
                            for insight in insight_list:
                                insight_type = insight.get(
                                    "type", "suggestion"
                                )
                                if insight_type not in (
                                    "alert", "scope", "suggestion"
                                ):
                                    insight_type = "suggestion"
                                db.add(Insight(
                                    meeting_id=meeting_id,
                                    type=InsightType(insight_type),
                                    content=insight.get("content", ""),
                                    confidence=insight.get(
                                        "confidence", 0.5
                                    ),
                                    sources=insight.get("sources", []),
                                    agent_source=insight.get(
                                        "agent_source"
                                    ),
                                    target_roles=insight.get(
                                        "target_roles"
                                    ),
                                    insight_subtype=insight.get("subtype"),
                                ))
                                await db.commit()

                                # Role-filtered delivery for agent insights
                                target_roles = insight.get("target_roles")
                                conf = insight.get("confidence", 0.5)
                                msg = {
                                    "type": "insight",
                                    "payload": insight,
                                }
                                if target_roles:
                                    await meeting_manager.broadcast_role_filtered(
                                        meeting_id, msg,
                                        target_roles=target_roles,
                                        confidence=conf,
                                    )
                                else:
                                    await meeting_manager.broadcast(
                                        meeting_id, msg,
                                    )

        session = DeepgramSession(on_transcription=on_transcription)
        started = await session.start()
        if started:
            _deepgram_sessions[meeting_id] = session
            logger.info("deepgram_session_created", meeting_id=str(meeting_id))
        else:
            logger.warning("deepgram_unavailable", meeting_id=str(meeting_id))

    await meeting_manager.broadcast(meeting_id, {
        "type": "meeting_status",
        "payload": {"status": "recording"},
    })

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "audio_chunk":
                payload = data.get("payload", {})
                audio_b64 = payload.get("audio", "")
                dg_session = _deepgram_sessions.get(meeting_id)
                if dg_session and audio_b64:
                    dg_session.send_audio_base64(audio_b64)

            elif msg_type == "end_meeting":
                dg_session = _deepgram_sessions.pop(meeting_id, None)
                if dg_session:
                    await dg_session.stop()
                clear_buffer(meeting_id)
                await meeting_manager.broadcast(meeting_id, {
                    "type": "meeting_status",
                    "payload": {"status": "ended"},
                })

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        meeting_manager.disconnect(meeting_id, websocket)
        if meeting_manager.get_connection_count(meeting_id) == 0:
            dg_session = _deepgram_sessions.pop(meeting_id, None)
            if dg_session:
                await dg_session.stop()
            clear_buffer(meeting_id)
            _meeting_projects.pop(meeting_id, None)
        logger.info("ws_client_disconnected", meeting_id=str(meeting_id))
    except Exception:
        meeting_manager.disconnect(meeting_id, websocket)
        logger.exception("ws_error", meeting_id=str(meeting_id))
