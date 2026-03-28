"""Tests for RAG pipeline with mocked LLM and embedding APIs."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.services.chunking import chunk_text
from app.services.llm import generate_insight
from app.services.rag import clear_buffer


class MockResponse:
    """Mock httpx response."""

    def __init__(self, status_code: int, data: dict) -> None:
        self.status_code = status_code
        self._data = data
        self.text = json.dumps(data)

    def json(self) -> dict:
        return self._data


@pytest.mark.asyncio
async def test_generate_insight_with_mocked_llm() -> None:
    """LLM returns valid JSON insight → parsed correctly."""
    llm_response = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "type": "alert",
                        "content": "NotificationDispatcher needs v3 migration",
                        "confidence": 0.92,
                        "sources": ["architecture.md"],
                    })
                }
            }
        ]
    }

    mock_resp = MockResponse(200, llm_response)

    with patch("app.services.llm.settings") as mock_settings:
        mock_settings.llm_api_key = "test-key"
        mock_settings.llm_model = "test-model"
        mock_settings.llm_fallback_model = "test-fallback"
        mock_settings.llm_base_url = "https://api.test.com/v1"

        with patch("app.services.llm.AsyncClient") as mock_client_cls:
            mock_client_instance = AsyncMock()
            mock_client_instance.post = AsyncMock(return_value=mock_resp)
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client_instance

            result = await generate_insight(
                "El cliente quiere cambiar las notificaciones push",
                ["NotificationDispatcher usa Firebase Cloud Messaging"],
            )

    assert result is not None
    assert result["type"] == "alert"
    assert "NotificationDispatcher" in result["content"]
    assert result["confidence"] == 0.92


@pytest.mark.asyncio
async def test_generate_insight_returns_none_for_type_none() -> None:
    """LLM returns type 'none' → returns None."""
    llm_response = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "type": "none",
                        "content": "",
                        "confidence": 0,
                        "sources": [],
                    })
                }
            }
        ]
    }
    mock_resp = MockResponse(200, llm_response)

    with patch("app.services.llm.settings") as mock_settings:
        mock_settings.llm_api_key = "test-key"
        mock_settings.llm_model = "test-model"
        mock_settings.llm_fallback_model = "test-fallback"
        mock_settings.llm_base_url = "https://api.test.com/v1"

        with patch("app.services.llm.AsyncClient") as mock_client_cls:
            mock_client_instance = AsyncMock()
            mock_client_instance.post = AsyncMock(return_value=mock_resp)
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client_instance

            result = await generate_insight("Hola, buenos dias", [])

    assert result is None


@pytest.mark.asyncio
async def test_generate_insight_fallback_on_rate_limit() -> None:
    """LLM returns 429 → falls back to secondary model."""
    rate_limited = MockResponse(429, {"error": "rate limited"})
    success = MockResponse(
        200,
        {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "type": "suggestion",
                            "content": "Fallback insight",
                            "confidence": 0.7,
                            "sources": [],
                        })
                    }
                }
            ]
        },
    )

    call_count = 0

    async def mock_post(*args, **kwargs):  # type: ignore[no-untyped-def]
        nonlocal call_count
        call_count += 1
        return rate_limited if call_count == 1 else success

    with patch("app.services.llm.settings") as mock_settings:
        mock_settings.llm_api_key = "test-key"
        mock_settings.llm_model = "primary-model"
        mock_settings.llm_fallback_model = "fallback-model"
        mock_settings.llm_base_url = "https://api.test.com/v1"

        with patch("app.services.llm.AsyncClient") as mock_client_cls:
            mock_client_instance = AsyncMock()
            mock_client_instance.post = mock_post
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client_instance

            result = await generate_insight("Test transcription", ["context"])

    assert result is not None
    assert result["type"] == "suggestion"
    assert call_count == 2  # First call rate limited, second succeeded


def test_chunking_and_rag_buffer() -> None:
    """Verify chunking produces valid chunks and buffer management works."""
    text = "This is important context about the project. " * 100
    chunks = chunk_text(text)
    assert len(chunks) > 1
    # Buffer management
    import uuid

    meeting_id = uuid.uuid4()
    clear_buffer(meeting_id)  # No error on non-existent
