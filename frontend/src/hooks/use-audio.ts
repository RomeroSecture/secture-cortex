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
 * Captures raw PCM linear16 audio at 16kHz using AudioContext + ScriptProcessor.
 * This format is directly compatible with Deepgram's WebSocket API.
 */
export function useAudio({ onAudioChunk }: UseAudioOptions): UseAudioReturn {
  const [isCapturing, setIsCapturing] = useState(false);
  const [hasMic, setHasMic] = useState(false);
  const [hasTab, setHasTab] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const micStreamRef = useRef<MediaStream | null>(null);
  const tabStreamRef = useRef<MediaStream | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);

  const startCapture = useCallback(async () => {
    setError(null);

    // Use default system sample rate (48kHz) — Deepgram handles resampling
    // Forcing 16kHz breaks tab audio capture (different sample rate domains)
    const audioCtx = new AudioContext();
    audioCtxRef.current = audioCtx;

    // ScriptProcessor to capture raw PCM samples
    const processor = audioCtx.createScriptProcessor(4096, 1, 1);
    processorRef.current = processor;

    processor.onaudioprocess = (e) => {
      const float32 = e.inputBuffer.getChannelData(0);
      // Convert float32 [-1,1] to int16 PCM (linear16)
      const int16 = new Int16Array(float32.length);
      for (let i = 0; i < float32.length; i++) {
        const s = Math.max(-1, Math.min(1, float32[i]));
        int16[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
      }
      // Encode as base64
      const bytes = new Uint8Array(int16.buffer);
      let binary = "";
      for (let i = 0; i < bytes.length; i++) {
        binary += String.fromCharCode(bytes[i]);
      }
      const base64 = btoa(binary);
      onAudioChunk("mic", base64);
    };

    // Channel 1: Microphone
    try {
      const micStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
        },
      });
      micStreamRef.current = micStream;
      const micSource = audioCtx.createMediaStreamSource(micStream);
      micSource.connect(processor);
      processor.connect(audioCtx.destination);
      setHasMic(true);
    } catch (err) {
      setError("Microphone access denied");
      console.error("Mic capture failed:", err);
      return;
    }

    // Channel 2: Tab/screen audio (optional)
    // User MUST check "Share tab audio" in the browser dialog
    try {
      const tabStream = await navigator.mediaDevices.getDisplayMedia({
        audio: true,
        video: true, // Required by Chrome to enable audio option
      });
      // Keep video tracks alive (stopping them kills audio in some browsers)
      // Just disable them so they don't consume resources
      tabStream.getVideoTracks().forEach((track) => {
        track.enabled = false;
      });

      const audioTracks = tabStream.getAudioTracks();
      console.log("Tab audio tracks:", audioTracks.length);

      if (audioTracks.length > 0) {
        tabStreamRef.current = tabStream;
        const tabSource = audioCtx.createMediaStreamSource(tabStream);
        tabSource.connect(processor);
        setHasTab(true);
      }
    } catch {
      console.warn("Tab audio not available — mic only");
    }

    setIsCapturing(true);
  }, [onAudioChunk]);

  const stopCapture = useCallback(() => {
    processorRef.current?.disconnect();
    audioCtxRef.current?.close();
    micStreamRef.current?.getTracks().forEach((t) => t.stop());
    tabStreamRef.current?.getTracks().forEach((t) => t.stop());
    processorRef.current = null;
    audioCtxRef.current = null;
    micStreamRef.current = null;
    tabStreamRef.current = null;
    setIsCapturing(false);
    setHasMic(false);
    setHasTab(false);
  }, []);

  return { isCapturing, hasMic, hasTab, startCapture, stopCapture, error };
}
