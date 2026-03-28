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

/**
 * WebSocket hook resilient to React Strict Mode double-mount.
 *
 * Uses useRef for the WS instance so it survives the unmount/remount
 * cycle. Only creates a new connection if there isn't one already.
 */
export function useWebSocket({
  url,
  onMessage,
  reconnect = true,
  maxRetries = 5,
}: UseWebSocketOptions): UseWebSocketReturn {
  const wsRef = useRef<WebSocket | null>(null);
  const retriesRef = useRef(0);
  const mountedRef = useRef(true);
  const [isConnected, setIsConnected] = useState(false);

  const onMessageRef = useRef(onMessage);
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  useEffect(() => {
    mountedRef.current = true;

    // Don't connect if URL is empty (waiting for params)
    if (!url) return;

    // If WS already exists and is open/connecting, don't create another
    if (
      wsRef.current &&
      (wsRef.current.readyState === WebSocket.OPEN ||
        wsRef.current.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }

    const doConnect = () => {
      if (!mountedRef.current) return;
      if (
        wsRef.current &&
        (wsRef.current.readyState === WebSocket.OPEN ||
          wsRef.current.readyState === WebSocket.CONNECTING)
      ) {
        return;
      }

      const ws = new WebSocket(url);

      ws.onopen = () => {
        if (!mountedRef.current) {
          ws.close();
          return;
        }
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
        // Only update state if this is still our active WS
        if (wsRef.current === ws) {
          setIsConnected(false);
          wsRef.current = null;
        }

        if (mountedRef.current && reconnect && retriesRef.current < maxRetries) {
          const delay = Math.min(1000 * 2 ** retriesRef.current, 30000);
          retriesRef.current += 1;
          setTimeout(doConnect, delay);
        }
      };

      ws.onerror = () => {
        ws.close();
      };

      wsRef.current = ws;
    };

    doConnect();

    return () => {
      mountedRef.current = false;
      // Don't close on cleanup — let the ref survive Strict Mode remount
      // The WS will be reused on the next mount
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url]);

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
    mountedRef.current = false;
    wsRef.current?.close();
    wsRef.current = null;
  }, [maxRetries]);

  return { isConnected, send, sendRaw, close };
}
