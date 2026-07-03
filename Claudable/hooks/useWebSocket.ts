/**
 * Stream Hook (Formerly WebSocket)
 * Manages SSE connection for real-time updates for Vercel deployment compatibility
 */
import { useEffect, useRef, useCallback, useState } from 'react';
import { WEBSOCKET_CONFIG } from '@/lib/config/constants';
import type { ChatMessage, RealtimeEvent, RealtimeStatus } from '@/types';

interface StreamOptions {
  projectId: string;
  onMessage?: (message: ChatMessage) => void;
  onStatus?: (status: string, data?: RealtimeStatus | Record<string, unknown>, requestId?: string) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Error) => void;
}

export function useWebSocket({
  projectId,
  onMessage,
  onStatus,
  onConnect,
  onDisconnect,
  onError
}: StreamOptions) {
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const connectionAttemptsRef = useRef(0);
  const shouldReconnectRef = useRef(true);
  const manualCloseRef = useRef(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  
  const handlersRef = useRef({
    onMessage,
    onStatus,
    onConnect,
    onDisconnect,
    onError,
  });

  useEffect(() => {
    handlersRef.current = {
      onMessage,
      onStatus,
      onConnect,
      onDisconnect,
      onError,
    };
  }, [onMessage, onStatus, onConnect, onDisconnect, onError]);

  const connect = useCallback(() => {
    const existing = eventSourceRef.current;
    if (existing) {
      if (
        existing.readyState === EventSource.OPEN ||
        existing.readyState === EventSource.CONNECTING
      ) {
        return;
      }
      try {
        existing.close();
      } catch {}
      eventSourceRef.current = null;
    }

    if (!shouldReconnectRef.current) {
      return;
    }

    setIsConnecting(true);
    const endpoint = `/api/chat/${projectId}/stream`;
    const es = new EventSource(endpoint);
    manualCloseRef.current = false;
    let openStabilizeTimeout: NodeJS.Timeout;

    es.onopen = () => {
      setIsConnected(true);
      setIsConnecting(false);
      openStabilizeTimeout = setTimeout(() => {
        connectionAttemptsRef.current = 0;
      }, 2000);
      handlersRef.current.onConnect?.();
    };

    es.onmessage = (event) => {
      try {
        const envelope = JSON.parse(event.data) as RealtimeEvent;
        const { onMessage: handleMessage, onStatus: handleStatus, onError: handleError } =
          handlersRef.current;

        switch (envelope.type) {
          case 'message':
            if (envelope.data && handleMessage) {
              handleMessage(envelope.data);
            }
            break;
          case 'status':
            if (envelope.data && handleStatus) {
              handleStatus(envelope.data.status, envelope.data, envelope.data.requestId);
            }
            break;
          case 'error': {
            const message = envelope.error ?? 'Realtime stream error';
            const rawData = envelope.data as Record<string, unknown> | undefined;
            const requestId = rawData?.requestId ?? rawData?.request_id;
            const payload: RealtimeStatus = {
              status: 'error',
              message,
              ...(typeof requestId === 'string' ? { requestId } : {}),
            };
            handleStatus?.('error', payload, typeof requestId === 'string' ? requestId : undefined);
            handleError?.(new Error(message));
            break;
          }
          case 'connected':
            if (handleStatus) {
              const payload: RealtimeStatus = {
                status: 'connected',
                message: 'Realtime channel connected',
                sessionId: envelope.data.sessionId,
              };
              handleStatus('connected', payload, envelope.data.sessionId);
            }
            break;
          case 'preview_error':
          case 'preview_success':
            if (handleStatus) {
              const payload: RealtimeStatus = {
                status: envelope.type,
                message: envelope.data?.message,
                metadata: envelope.data?.severity
                  ? { severity: envelope.data.severity }
                  : undefined,
              };
              handleStatus(envelope.type, payload);
            }
            break;
          case 'heartbeat':
            // Handled automatically by EventSource keeping connection alive
            break;
          default: {
            const fallback = envelope as unknown as { type: string };
            handleStatus?.(fallback.type, envelope as unknown as Record<string, unknown>);
            break;
          }
        }
      } catch (error) {
        console.error('Failed to parse SSE message:', error);
      }
    };

    es.onerror = (error) => {
      if (openStabilizeTimeout) clearTimeout(openStabilizeTimeout);
      if (manualCloseRef.current) {
        setIsConnecting(false);
        return;
      }
      
      console.warn('❌ SSE stream error');
      setIsConnecting(false);
      setIsConnected(false);
      es.close();
      eventSourceRef.current = null;
      handlersRef.current.onError?.(new Error(`SSE connection error to ${endpoint}`));
      handlersRef.current.onDisconnect?.();

      if (shouldReconnectRef.current) {
        const attempts = connectionAttemptsRef.current + 1;
        connectionAttemptsRef.current = attempts;

        let delay: number;
        if (attempts > WEBSOCKET_CONFIG.MAX_RECONNECT_ATTEMPTS) {
          const longDelay = 30000 + Math.random() * 30000;
          delay = longDelay;
          console.warn(`[Stream] Max reconnection attempts reached, retrying every 30-60s (attempt ${attempts})`);
        } else {
          const exponentialDelay = Math.min(
            WEBSOCKET_CONFIG.BASE_RECONNECT_DELAY * Math.pow(2, attempts - 1),
            WEBSOCKET_CONFIG.MAX_RECONNECT_DELAY
          );
          delay = exponentialDelay + Math.random() * 1000;
          console.log(`[Stream] Reconnecting in ${Math.round(delay)}ms (attempt ${attempts})`);
        }

        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, delay);
      }
    };

    eventSourceRef.current = es;
  }, [projectId]);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    manualCloseRef.current = true;
    setIsConnecting(false);
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((data: any) => {
    // SSE is unidirectional (server -> client).
    // Client -> server is handled via REST APIs (e.g. POST /api/chat/.../act)
    console.warn('sendMessage is not supported via SSE. Use REST endpoints instead.');
  }, []);

  const manualReconnect = useCallback(() => {
    console.log('[Stream] Manual reconnect triggered');
    shouldReconnectRef.current = true;
    connectionAttemptsRef.current = 0;
    disconnect();
    setTimeout(() => connect(), 100);
  }, [disconnect, connect]);

  useEffect(() => {
    shouldReconnectRef.current = true;
    manualCloseRef.current = false;
    connectionAttemptsRef.current = 0;
    connect();
    
    return () => {
      disconnect();
    };
  }, [projectId, disconnect, connect]);

  return {
    isConnected,
    isConnecting,
    connect,
    disconnect,
    sendMessage,
    manualReconnect
  };
}
