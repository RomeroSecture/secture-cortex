"""API v1 router — aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.auth import router as auth_router
from app.api.v1.context import router as context_router
from app.api.v1.conversation_events import router as events_router
from app.api.v1.insights import router as insights_router
from app.api.v1.meeting_outputs import router as meeting_outputs_router
from app.api.v1.meetings import router as meetings_router
from app.api.v1.project_analytics import router as project_analytics_router
from app.api.v1.projects import router as projects_router

api_router = APIRouter()
api_router.include_router(admin_router)
api_router.include_router(auth_router)
api_router.include_router(projects_router)
api_router.include_router(context_router)
api_router.include_router(meetings_router)
api_router.include_router(meeting_outputs_router)
api_router.include_router(events_router)
api_router.include_router(analytics_router)
api_router.include_router(project_analytics_router)
api_router.include_router(insights_router)


@api_router.get("/status")
async def api_status() -> dict:
    """API status check."""
    return {"data": {"status": "operational", "version": "0.1.0"}}
