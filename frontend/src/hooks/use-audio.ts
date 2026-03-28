"use client";

import { useCallback, useRef, useState } from "react";

interface UseAudioOptions {
  onAudioChunk: (channel: "mic" | "tab", audioBase64: string) => void;
}

interface UseAudioReturn {
  isCapturing: boolean;
  hasMic: boolean;
  hasTab: boolean;
  startCapture: () => Promise<void>;
  stopCapture: () => void;
  error: string | null;
}

/**
 * Captures mic and tab audio as SEPARATE channels.
 * Each channel is sent independently so the backend can
 * interleave them as stereo for Deepgram multichannel.
 */

function encodeChunk(float32: Float32Array): string {
  const int16 = new Int16Array(float32.length);
  for (let i = 0; i < float32.length; i++) {
    const s = Math.max(-1, Math.min(1, float32[i]));
    int16[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }
  const bytes = new Uint8Array(int16.buffer);
  let binary = "";
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

export function useAudio({ onAudioChunk }: UseAudioOptions): UseAudioReturn {
  const [isCapturing, setIsCapturing] = useState(false);
  const [hasMic, setHasMic] = useState(false);
  const [hasTab, setHasTab] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const micStreamRef = useRef<MediaStream | null>(null);
  const tabStreamRef = useRef<MediaStream | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const micProcessorRef = useRef<ScriptProcessorNode | null>(null);
  const tabProcessorRef = useRef<ScriptProcessorNode | null>(null);

  const startCapture = useCallback(async () => {
    setError(null);

    const audioCtx = new AudioContext();
    audioCtxRef.current = audioCtx;

    // Mic processor — channel "mic"
    const micProcessor = audioCtx.createScriptProcessor(4096, 1, 1);
    micProcessorRef.current = micProcessor;
    micProcessor.onaudioprocess = (e) => {
      onAudioChunk("mic", encodeChunk(e.inputBuffer.getChannelData(0)));
    };

    // Microphone
    try {
      const micStream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true },
      });
      micStreamRef.current = micStream;
      const micSource = audioCtx.createMediaStreamSource(micStream);
      micSource.connect(micProcessor);
      micProcessor.connect(audioCtx.destination);
      setHasMic(true);
    } catch {
      setError("Acceso al micrófono denegado");
      return;
    }

    // Tab audio — channel "tab"
    try {
      const tabStream = await navigator.mediaDevices.getDisplayMedia({
        audio: {
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false,
        },
        video: true,
      });

      // Minimize video overhead
      tabStream.getVideoTracks().forEach((track) => {
        track.applyConstraints({
          width: 1,
          height: 1,
          frameRate: 1,
        }).catch(() => {});
      });

      const audioTracks = tabStream.getAudioTracks();
      if (audioTracks.length > 0) {
        tabStreamRef.current = tabStream;
        const tabProcessor = audioCtx.createScriptProcessor(4096, 1, 1);
        tabProcessorRef.current = tabProcessor;
        tabProcessor.onaudioprocess = (e) => {
          onAudioChunk("tab", encodeChunk(e.inputBuffer.getChannelData(0)));
        };
        const tabSource = audioCtx.createMediaStreamSource(tabStream);
        tabSource.connect(tabProcessor);
        tabProcessor.connect(audioCtx.destination);
        setHasTab(true);
      } else {
        setError(
          "Sin audio de pestaña. Selecciona una pestaña de Chrome y marca 'Compartir audio'.",
        );
        tabStream.getTracks().forEach((t) => t.stop());
      }
    } catch {
      // Tab audio optional — mic only mode
    }

    setIsCapturing(true);
  }, [onAudioChunk]);

  const stopCapture = useCallback(() => {
    micProcessorRef.current?.disconnect();
    tabProcessorRef.current?.disconnect();
    audioCtxRef.current?.close();
    micStreamRef.current?.getTracks().forEach((t) => t.stop());
    tabStreamRef.current?.getTracks().forEach((t) => t.stop());
    micProcessorRef.current = null;
    tabProcessorRef.current = null;
    audioCtxRef.current = null;
    micStreamRef.current = null;
    tabStreamRef.current = null;
    setIsCapturing(false);
    setHasMic(false);
    setHasTab(false);
  }, []);

  return { isCapturing, hasMic, hasTab, startCapture, stopCapture, error };
}
