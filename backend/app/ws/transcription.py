"""WebSocket endpoint for audio streaming, transcription, and RAG insights."""

import asyncio
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

# Lock to prevent race condition on session creation
_session_lock = asyncio.Lock()

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

    # Start Deepgram session — lock prevents race condition with concurrent connects
    await _ensure_deepgram_session(meeting_id)

    # Send actual meeting status (not hardcoded "recording")
    from app.repositories.meeting import get_meeting_by_id

    async with async_session() as status_db:
        meeting_record = await get_meeting_by_id(status_db, meeting_id)
    current_status = (
        meeting_record.status.value
        if meeting_record
        else "recording"
    )
    await meeting_manager.broadcast(meeting_id, {
        "type": "meeting_status",
        "payload": {"status": current_status},
    })

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "audio_chunk":
                payload = data.get("payload", {})
                audio_b64 = payload.get("audio", "")
                ch_name = payload.get("channel", "mic")
                ch_num = 1 if ch_name == "tab" else 0
                dg_session = _deepgram_sessions.get(meeting_id)
                if dg_session and audio_b64:
                    if ch_num == 1:
                        await dg_session.ensure_tab_channel()
                    dg_session.send_audio_base64(audio_b64, ch_num)

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


async def _ensure_deepgram_session(meeting_id: uuid.UUID) -> None:
    """Create a single Deepgram session per meeting, protected by lock."""
    async with _session_lock:
        if meeting_id in _deepgram_sessions:
            return

        async def on_transcription(msg: dict) -> None:
            """Broadcast transcription + trigger RAG pipeline."""
            await meeting_manager.broadcast(meeting_id, msg)

            t_payload = msg.get("payload", {})
            text = t_payload.get("text", "")
            is_final = t_payload.get("is_final", False)
            pid = _meeting_projects.get(meeting_id)

            if text:
                async with async_session() as db:
                    if is_final:
                        db.add(Transcription(
                            meeting_id=meeting_id,
                            speaker=t_payload.get("speaker", "Speaker"),
                            text=text,
                            is_final=True,
                        ))
                        await db.commit()

                    if pid:
                        roles = meeting_manager.get_connected_roles(
                            meeting_id,
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
                                i_type = insight.get("type", "suggestion")
                                if i_type not in (
                                    "alert", "scope", "suggestion",
                                ):
                                    i_type = "suggestion"
                                db.add(Insight(
                                    meeting_id=meeting_id,
                                    type=InsightType(i_type),
                                    content=insight.get("content", ""),
                                    confidence=insight.get(
                                        "confidence", 0.5,
                                    ),
                                    sources=insight.get("sources", []),
                                    agent_source=insight.get(
                                        "agent_source",
                                    ),
                                    target_roles=insight.get(
                                        "target_roles",
                                    ),
                                    insight_subtype=insight.get(
                                        "subtype",
                                    ),
                                ))
                                await db.commit()

                                target_roles = insight.get("target_roles")
                                conf = insight.get("confidence", 0.5)
                                i_msg = {
                                    "type": "insight",
                                    "payload": insight,
                                }
                                if target_roles:
                                    await meeting_manager.broadcast_role_filtered(
                                        meeting_id, i_msg,
                                        target_roles=target_roles,
                                        confidence=conf,
                                    )
                                else:
                                    await meeting_manager.broadcast(
                                        meeting_id, i_msg,
                                    )

        session = DeepgramSession(on_transcription=on_transcription)
        started = await session.start()
        if started:
            _deepgram_sessions[meeting_id] = session
            logger.info(
                "deepgram_session_created",
                meeting_id=str(meeting_id),
            )
        else:
            logger.warning(
                "deepgram_unavailable",
                meeting_id=str(meeting_id),
            )
