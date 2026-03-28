"""Deepgram real-time transcription — async websockets (no SDK).

Two independent Deepgram sessions: one for mic, one for tab audio.
Each produces its own transcription with a fixed speaker label.
No interleaving, no multichannel complexity.
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


class SingleChannelSession:
    """One Deepgram WS connection for a single audio channel."""

    def __init__(
        self,
        speaker_label: str,
        on_transcription: TranscriptionCallback,
    ) -> None:
        self._speaker = speaker_label
        self._on_transcription = on_transcription
        self._ws: Any = None
        self._retries = 0
        self._stopped = False
        self._listen_task: asyncio.Task | None = None

    async def start(self) -> bool:
        """Open connection to Deepgram."""
        if not settings.deepgram_api_key:
            return False
        self._stopped = False
        return await self._connect()

    async def _connect(self) -> bool:
        try:
            params = {
                "model": "nova-3",
                "language": "multi",
                "encoding": "linear16",
                "sample_rate": "48000",
                "channels": "1",
                "smart_format": "true",
                "punctuate": "true",
                "interim_results": "true",
                "endpointing": "400",
                "utterance_end_ms": "1500",
                "vad_events": "true",
            }
            url = f"{DEEPGRAM_WS_URL}?{urllib.parse.urlencode(params)}"
            headers = {
                "Authorization": f"Token {settings.deepgram_api_key}",
            }
            self._ws = await websockets.connect(
                url, additional_headers=headers,
            )
            self._retries = 0
            logger.info(
                "deepgram_channel_connected",
                speaker=self._speaker,
            )
            self._listen_task = asyncio.create_task(self._listen())
            return True
        except Exception:
            logger.exception("deepgram_connect_failed",
                             speaker=self._speaker)
            return False

    async def _listen(self) -> None:
        try:
            async for raw_msg in self._ws:
                if self._stopped:
                    break
                try:
                    msg = json.loads(raw_msg)
                    if msg.get("type") != "Results":
                        continue

                    alt = msg.get("channel", {}).get(
                        "alternatives", [{}],
                    )
                    transcript = alt[0].get("transcript", "")
                    if not transcript.strip():
                        continue

                    is_final = msg.get("is_final", False)
                    speech_final = msg.get("speech_final", False)

                    await self._on_transcription({
                        "type": "transcription",
                        "payload": {
                            "speaker": self._speaker,
                            "text": transcript,
                            "is_final": is_final or speech_final,
                        },
                    })
                except json.JSONDecodeError:
                    continue
                except Exception:
                    logger.exception("deepgram_message_error")

        except websockets.exceptions.ConnectionClosed:
            if not self._stopped:
                logger.warning(
                    "deepgram_connection_lost",
                    speaker=self._speaker,
                )
                await self._reconnect()
        except Exception:
            if not self._stopped:
                logger.exception("deepgram_listen_error")
                await self._reconnect()

    async def _reconnect(self) -> None:
        if self._stopped or self._retries >= MAX_RETRIES:
            return
        self._retries += 1
        delay = min(BASE_BACKOFF_S * (2 ** (self._retries - 1)), 30.0)
        logger.warning(
            "deepgram_reconnecting",
            speaker=self._speaker,
            retry=self._retries,
            delay=delay,
        )
        await asyncio.sleep(delay)
        await self._connect()

    def send_audio_base64(self, audio_b64: str) -> None:
        """Decode base64 and send to Deepgram."""
        if not self._ws or self._stopped:
            return
        try:
            audio_bytes = base64.b64decode(audio_b64)
            asyncio.get_running_loop().create_task(
                self._ws.send(audio_bytes),
            )
        except Exception:
            pass

    async def stop(self) -> None:
        self._stopped = True
        if self._listen_task:
            self._listen_task.cancel()
        if self._ws:
            with contextlib.suppress(Exception):
                await self._ws.close()
        self._ws = None


class DeepgramSession:
    """Manages one or two Deepgram channels (mic + optional tab)."""

    def __init__(
        self, on_transcription: TranscriptionCallback,
    ) -> None:
        self._on_transcription = on_transcription
        self._mic: SingleChannelSession | None = None
        self._tab: SingleChannelSession | None = None

    async def start(self, **_kwargs: Any) -> bool:
        """Start mic channel. Tab channel starts on first tab audio."""
        self._mic = SingleChannelSession(
            "Speaker 0", self._on_transcription,
        )
        return await self._mic.start()

    async def ensure_tab_channel(self) -> None:
        """Lazily start tab channel on first tab audio chunk."""
        if self._tab is not None:
            return
        self._tab = SingleChannelSession(
            "Speaker 1", self._on_transcription,
        )
        started = await self._tab.start()
        if not started:
            self._tab = None

    def send_audio_base64(
        self, audio_b64: str, channel: int = 0,
    ) -> None:
        """Route audio to the correct Deepgram channel."""
        if channel == 1 and self._tab:
            self._tab.send_audio_base64(audio_b64)
        elif self._mic:
            self._mic.send_audio_base64(audio_b64)

    async def stop(self) -> None:
        if self._mic:
            await self._mic.stop()
        if self._tab:
            await self._tab.stop()
        logger.info("deepgram_stopped")
