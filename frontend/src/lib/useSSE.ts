"use client";

import { useState, useCallback, useRef } from "react";

export interface SSEEvent {
  event: string;
  data: any;
}

interface UseSSEOptions {
  onMessage?: (event: SSEEvent) => void;
  onError?: (error: Event) => void;
  onComplete?: () => void;
}

export function useSSE(url: string, options: UseSSEOptions = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);

  const connect = useCallback(
    (body?: any) => {
      // Close existing connection
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      // For POST-based SSE, use fetch with streaming
      if (body) {
        const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
        const headers: Record<string, string> = {
          "Content-Type": "application/json",
          Accept: "text/event-stream",
        };
        if (token) {
          headers["Authorization"] = `Bearer ${token}`;
        }

        fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}${url}`, {
          method: "POST",
          headers,
          body: JSON.stringify(body),
        })
          .then(async (response) => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            setIsConnected(true);

            const reader = response.body?.getReader();
            if (!reader) return;

            const decoder = new TextDecoder();
            let buffer = "";

            while (true) {
              const { done, value } = await reader.read();
              if (done) break;

              buffer += decoder.decode(value, { stream: true });
              const lines = buffer.split("\n");
              buffer = lines.pop() || "";

              let currentEvent = "";
              for (const line of lines) {
                if (line.startsWith("event: ")) {
                  currentEvent = line.slice(7).trim();
                } else if (line.startsWith("data: ")) {
                  try {
                    const data = JSON.parse(line.slice(6));
                    const event: SSEEvent = { event: currentEvent, data };
                    setEvents((prev) => [...prev, event]);
                    options.onMessage?.(event);
                    if (currentEvent === "done") {
                      options.onComplete?.();
                      setIsConnected(false);
                    }
                  } catch {
                    // Skip parse errors
                  }
                }
              }
            }
            options.onComplete?.();
            setIsConnected(false);
          })
          .catch((err) => {
            options.onError?.(err);
            setIsConnected(false);
          });
      } else {
        // GET-based SSE
        const es = new EventSource(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}${url}`
        );
        eventSourceRef.current = es;

        es.onopen = () => setIsConnected(true);

        es.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            const sseEvent: SSEEvent = { event: event.type, data };
            setEvents((prev) => [...prev, sseEvent]);
            options.onMessage?.(sseEvent);
          } catch {
            // Skip
          }
        };

        es.addEventListener("done", () => {
          options.onComplete?.();
          setIsConnected(false);
          es.close();
        });

        es.onerror = (err) => {
          options.onError?.(err);
          setIsConnected(false);
        };
      }
    },
    [url, options]
  );

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsConnected(false);
  }, []);

  return { isConnected, events, connect, disconnect };
}
