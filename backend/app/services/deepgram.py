"""Deepgram real-time transcription — async websockets (no SDK).

Direct async WebSocket connection to Deepgram Nova-3.
Bypasses the sync SDK which conflicts with FastAPI's async event loop.
"""

import asyncio
import base64
import contextlib
import json
import urllib.parse
from collections.abc import Callable, Coroutine
from typing import Any

import structlog
import websockets

from app.config import settings

logger = structlog.get_logger()

TranscriptionCallback = Callable[[dict], Coroutine[Any, Any, None]]

MAX_RETRIES = 5
BASE_BACKOFF_S = 1.0
DEEPGRAM_WS_URL = "wss://api.deepgram.com/v1/listen"


class DeepgramSession:
    """Async Deepgram live transcription session with auto-reconnect."""

    def __init__(self, on_transcription: TranscriptionCallback) -> None:
        self._on_transcription = on_transcription
        self._ws: Any = None
        self._retries = 0
        self._stopped = False
        self._listen_task: asyncio.Task | None = None

    async def start(self) -> bool:
        """Open the Deepgram WebSocket connection."""
        if not settings.deepgram_api_key:
            logger.warning("deepgram_api_key_not_set")
            return False
        self._stopped = False
        return await self._connect()

    async def _connect(self) -> bool:
        """Establish async WebSocket connection to Deepgram."""
        try:
            params = {
                "model": "nova-3",
                "language": "multi",
                "encoding": "linear16",
                "sample_rate": "48000",  # Browser AudioContext default
                "channels": "1",
                "diarize": "true",
                "interim_results": "true",
                "smart_format": "true",
                "punctuate": "true",
            }
            url = f"{DEEPGRAM_WS_URL}?{urllib.parse.urlencode(params)}"
            headers = {"Authorization": f"Token {settings.deepgram_api_key}"}

            self._ws = await websockets.connect(url, additional_headers=headers)
            self._retries = 0
            logger.info("deepgram_connected")

            # Start listening for transcription results in background
            self._listen_task = asyncio.create_task(self._listen_loop())
            return True

        except Exception:
            logger.exception("deepgram_connect_failed")
            return False

    async def _listen_loop(self) -> None:
        """Receive transcription results from Deepgram and forward via callback."""
        try:
            async for raw_msg in self._ws:
                if self._stopped:
                    break
                try:
                    msg = json.loads(raw_msg)
                    msg_type = msg.get("type", "")

                    if msg_type != "Results":
                        continue

                    channel = msg.get("channel", {})
                    alternatives = channel.get("alternatives", [])
                    if not alternatives:
                        continue

                    transcript = alternatives[0].get("transcript", "")
                    if not transcript.strip():
                        continue

                    is_final = msg.get("is_final", False)
                    speech_final = msg.get("speech_final", False)

                    # Extract speaker from words
                    words = alternatives[0].get("words", [])
                    speaker = "Speaker"
                    if words and "speaker" in words[0]:
                        speaker = f"Speaker {words[0]['speaker']}"

                    payload = {
                        "type": "transcription",
                        "payload": {
                            "speaker": speaker,
                            "text": transcript,
                            "is_final": is_final or speech_final,
                        },
                    }
                    await self._on_transcription(payload)

                except json.JSONDecodeError:
                    continue
                except Exception:
                    logger.exception("deepgram_message_error")

        except websockets.exceptions.ConnectionClosed:
            if not self._stopped:
                logger.warning("deepgram_connection_lost")
                await self._reconnect()
        except Exception:
            if not self._stopped:
                logger.exception("deepgram_listen_error")
                await self._reconnect()

    async def _reconnect(self) -> None:
        """Reconnect with exponential backoff."""
        if self._stopped or self._retries >= MAX_RETRIES:
            logger.error("deepgram_max_retries", retries=self._retries)
            return
        self._retries += 1
        delay = min(BASE_BACKOFF_S * (2 ** (self._retries - 1)), 30.0)
        logger.warning("deepgram_reconnecting", retry=self._retries, delay=delay)
        await asyncio.sleep(delay)
        await self._connect()

    def send_audio(self, audio_bytes: bytes) -> None:
        """Send raw PCM audio bytes to Deepgram."""
        if self._ws and not self._stopped:
            try:
                asyncio.get_running_loop().create_task(self._ws.send(audio_bytes))
            except Exception:
                logger.exception("deepgram_send_failed")

    def send_audio_base64(self, audio_b64: str) -> None:
        """Decode base64 audio and send to Deepgram."""
        try:
            audio_bytes = base64.b64decode(audio_b64)
            self.send_audio(audio_bytes)
        except Exception:
            logger.exception("deepgram_decode_failed")

    async def stop(self) -> None:
        """Close the Deepgram connection."""
        self._stopped = True
        if self._listen_task:
            self._listen_task.cancel()
        if self._ws:
            with contextlib.suppress(Exception):
                await self._ws.close()
            logger.info("deepgram_stopped")
        self._ws = None
