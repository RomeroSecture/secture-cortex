"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { WsMessage } from "@/types/websocket";

interface UseWebSocketOptions {
  url: string;
  onMessage?: (msg: WsMessage) => void;
  reconnect?: boolean;
  maxRetries?: number;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  send: (msg: WsMessage) => void;
  sendRaw: (data: string) => void;
  close: () => void;
}

export function useWebSocket({
  url,
  onMessage,
  reconnect = true,
  maxRetries = 5,
}: UseWebSocketOptions): UseWebSocketReturn {
  const wsRef = useRef<WebSocket | null>(null);
  const retriesRef = useRef(0);
  const connectRef = useRef<() => void>(() => {});
  const [isConnected, setIsConnected] = useState(false);

  const onMessageRef = useRef(onMessage);

  // Keep ref in sync without triggering reconnect
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  useEffect(() => {
    const doConnect = () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) return;

      const ws = new WebSocket(url);

      ws.onopen = () => {
        setIsConnected(true);
        retriesRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const msg: WsMessage = JSON.parse(event.data);
          onMessageRef.current?.(msg);
        } catch {
          console.error("Failed to parse WS message:", event.data);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        wsRef.current = null;

        if (reconnect && retriesRef.current < maxRetries) {
          const delay = Math.min(1000 * 2 ** retriesRef.current, 30000);
          retriesRef.current += 1;
          setTimeout(() => connectRef.current(), delay);
        }
      };

      ws.onerror = () => {
        ws.close();
      };

      wsRef.current = ws;
    };

    connectRef.current = doConnect;
    doConnect();

    return () => {
      wsRef.current?.close();
    };
  }, [url, reconnect, maxRetries]);

  const send = useCallback((msg: WsMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(msg));
    }
  }, []);

  const sendRaw = useCallback((data: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(data);
    }
  }, []);

  const close = useCallback(() => {
    retriesRef.current = maxRetries;
    wsRef.current?.close();
  }, [maxRetries]);

  return { isConnected, send, sendRaw, close };
}
