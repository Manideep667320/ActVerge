"use client";

import { useEffect, useRef, useCallback } from "react";
import { getStreamUrl } from "./api";
import { useActVergeStore } from "./store";
import type {
  SSEEvent,
  AgentNodeName,
  Verdict,
  ActionTrace,
  Evidence,
} from "./types";

const MAX_RETRIES = 5;
const BASE_DELAY_MS = 1000;

/**
 * Connects to the SSE stream for a given task and drives the Zustand store.
 * Handles node_start / node_complete / verdict / trace / evidence events.
 * Implements exponential-backoff reconnection.
 */
export function useSSE(taskId: string | null) {
  const esRef = useRef<EventSource | null>(null);
  const retriesRef = useRef(0);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const {
    updateNodeState,
    setVerdict,
    addTrace,
    addEvidence,
    setRawState,
    setSseConnected,
    setSseError,
    updateTask,
  } = useActVergeStore();

  const cleanup = useCallback(() => {
    if (esRef.current) {
      esRef.current.close();
      esRef.current = null;
    }
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  const handleEvent = useCallback(
    (taskId: string, parsed: SSEEvent) => {
      switch (parsed.type) {
        case "node_start":
          if (parsed.node) {
            updateNodeState(parsed.node as AgentNodeName, "running");
          }
          break;
        case "node_complete":
          if (parsed.node) {
            updateNodeState(parsed.node as AgentNodeName, "complete");
          }
          break;
        case "verdict":
          if (parsed.data) {
            setVerdict(parsed.data as Verdict);
            updateTask(taskId, { status: "complete" });
          }
          break;
        case "trace":
          if (parsed.data) {
            addTrace(parsed.data as ActionTrace);
          }
          break;
        case "state":
          if (parsed.data) {
            setRawState(parsed.data as Record<string, unknown>);
          }
          break;
        case "error":
          if (parsed.node) {
            updateNodeState(parsed.node as AgentNodeName, "error");
          }
          setSseError(
            (parsed.data as { message?: string })?.message ?? "Unknown error"
          );
          updateTask(taskId, { status: "error" });
          break;
        default:
          break;
      }
    },
    [updateNodeState, setVerdict, addTrace, setRawState, setSseError, updateTask]
  );

  const connect = useCallback(() => {
    if (!taskId) return;
    cleanup();

    const url = getStreamUrl(taskId);
    const es = new EventSource(url);
    esRef.current = es;

    es.onopen = () => {
      retriesRef.current = 0;
      setSseConnected(true);
      setSseError(null);
    };

    // Generic message handler (fallback)
    es.onmessage = (event: MessageEvent) => {
      try {
        const parsed: SSEEvent = JSON.parse(event.data as string);
        handleEvent(taskId, parsed);
      } catch (err) {
        console.warn("[SSE] Failed to parse message", err);
      }
    };

    // Named event listeners for each event type
    const addEventListener = (
      name: string,
      handler: (e: MessageEvent) => void
    ) => {
      es.addEventListener(name, handler as EventListener);
    };

    addEventListener("node_start", (event) => {
      try {
        const parsed: SSEEvent = JSON.parse(event.data as string);
        if (parsed.node) {
          updateNodeState(parsed.node as AgentNodeName, "running");
        }
      } catch {
        // ignore
      }
    });

    addEventListener("node_complete", (event) => {
      try {
        const parsed: SSEEvent = JSON.parse(event.data as string);
        if (parsed.node) {
          updateNodeState(parsed.node as AgentNodeName, "complete");
        }
      } catch {
        // ignore
      }
    });

    addEventListener("verdict", (event) => {
      try {
        const parsed: SSEEvent = JSON.parse(event.data as string);
        if (parsed.data) {
          setVerdict(parsed.data as Verdict);
          updateTask(taskId, { status: "complete" });
        }
      } catch {
        // ignore
      }
    });

    addEventListener("trace", (event) => {
      try {
        const parsed: SSEEvent = JSON.parse(event.data as string);
        if (parsed.data) {
          addTrace(parsed.data as ActionTrace);
        }
      } catch {
        // ignore
      }
    });

    addEventListener("evidence", (event) => {
      try {
        const parsed: SSEEvent = JSON.parse(event.data as string);
        if (parsed.data) {
          addEvidence(parsed.data as Evidence);
        }
      } catch {
        // ignore
      }
    });

    addEventListener("raw_state", (event) => {
      try {
        const parsed: SSEEvent = JSON.parse(event.data as string);
        if (parsed.data) {
          setRawState(parsed.data as Record<string, unknown>);
        }
      } catch {
        // ignore
      }
    });

    es.onerror = () => {
      setSseConnected(false);
      cleanup();

      if (retriesRef.current < MAX_RETRIES) {
        const delay = BASE_DELAY_MS * Math.pow(2, retriesRef.current);
        retriesRef.current += 1;
        console.warn(
          `[SSE] Connection lost. Reconnecting in ${delay}ms (attempt ${retriesRef.current}/${MAX_RETRIES})`
        );
        timeoutRef.current = setTimeout(connect, delay);
      } else {
        setSseError("Lost connection to server. Please refresh the page.");
      }
    };
  }, [
    taskId,
    cleanup,
    handleEvent,
    updateNodeState,
    setVerdict,
    addTrace,
    addEvidence,
    setRawState,
    setSseConnected,
    setSseError,
    updateTask,
  ]);

  useEffect(() => {
    if (!taskId) return;
    connect();
    return cleanup;
  }, [taskId, connect, cleanup]);
}
