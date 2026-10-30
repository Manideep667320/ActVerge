"use client";

import { useEffect } from "react";
import { useActVergeStore } from "@/lib/store";
import { useSSE } from "@/lib/sse";
import { fetchTask, fetchVerdict, fetchEvidence, fetchTrace, fetchTaskState } from "@/lib/api";
import VerdictBadge from "@/components/VerdictBadge";
import AgentGraph from "@/components/AgentGraph";
import StatusStream from "@/components/StatusStream";
import EvidencePanel from "@/components/EvidencePanel";
import RawStateViewer from "@/components/RawStateViewer";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Wifi, WifiOff, AlertCircle } from "lucide-react";
import Link from "next/link";
import { formatSafeDate } from "@/lib/utils";

interface Props {
  taskId: string;
}

export default function TaskDetailClient({ taskId }: Props) {
  const {
    activeTask,
    activeVerdict,
    activeTraces,
    activeEvidence,
    activeRawState,
    nodeStates,
    sseConnected,
    sseError,
    setActiveTask,
    setVerdict,
    addEvidence,
    addTrace,
    setRawState,
    clearActiveTask,
  } = useActVergeStore();

  // Connect SSE stream
  useSSE(taskId);

  // Load initial task data
  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const task = await fetchTask(taskId);
        if (!cancelled) setActiveTask(task);

        // If already complete, pre-load verdict + evidence + trace
        if (task.status === "complete" || task.status === "error") {
          try {
            const verdict = await fetchVerdict(taskId);
            if (!cancelled) setVerdict(verdict);
          } catch {
            // no verdict yet
          }

          try {
            const ev = await fetchEvidence(taskId);
            if (!cancelled) ev.forEach(addEvidence);
          } catch {
            // no evidence yet
          }

          try {
            const traces = await fetchTrace(taskId);
            if (!cancelled) traces.forEach(addTrace);
          } catch {
            // no trace yet
          }

          try {
            const rawState = await fetchTaskState(taskId);
            if (!cancelled && rawState) setRawState(rawState);
          } catch {
            // no state yet
          }
        }
      } catch (err) {
        console.error("Failed to load task", err);
      }
    }

    load();
    return () => {
      cancelled = true;
      clearActiveTask();
    };
  }, [taskId, setActiveTask, setVerdict, addEvidence, addTrace, setRawState, clearActiveTask]);

  const statusColor: Record<string, string> = {
    queued: "bg-gray-100 text-gray-600",
    running: "bg-blue-100 text-blue-700",
    interpreting: "bg-blue-100 text-blue-700",
    executing: "bg-indigo-100 text-indigo-700",
    observing: "bg-purple-100 text-purple-700",
    collecting_evidence: "bg-amber-100 text-amber-700",
    verifying: "bg-cyan-100 text-cyan-700",
    recovering: "bg-orange-100 text-orange-700",
    escalated: "bg-red-100 text-red-700",
    complete: "bg-green-100 text-green-700",
    error: "bg-red-100 text-red-700",
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Header */}
      <div className="border-b px-6 py-4 flex items-center gap-4 bg-card sticky top-0 z-10">
        <Link
          href="/"
          className="text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="font-semibold text-lg truncate">
              {activeTask?.user_task ?? "Loading…"}
            </h1>
            {activeTask && (
              <span
                className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  statusColor[activeTask.status] ?? "bg-gray-100 text-gray-600"
                }`}
              >
                {activeTask.status.replace(/_/g, " ")}
              </span>
            )}
          </div>
          {activeTask && (
            <p className="text-xs text-muted-foreground mt-0.5">
              ID: {activeTask.id} · {formatSafeDate(activeTask.created_at)}
            </p>
          )}
        </div>

        {/* SSE indicator */}
        <div className="flex items-center gap-2 shrink-0">
          {sseError ? (
            <span className="flex items-center gap-1 text-xs text-red-500">
              <AlertCircle className="h-3.5 w-3.5" />
              {sseError}
            </span>
          ) : sseConnected ? (
            <span className="flex items-center gap-1 text-xs text-green-600">
              <Wifi className="h-3.5 w-3.5" />
              Live
            </span>
          ) : (
            <span className="flex items-center gap-1 text-xs text-muted-foreground">
              <WifiOff className="h-3.5 w-3.5" />
              Connecting…
            </span>
          )}

          {/* Verdict badge */}
          {activeVerdict && (
            <VerdictBadge verdict={activeVerdict.verdict} size="md" />
          )}
        </div>
      </div>

      {/* Agent workflow graph */}
      <div className="h-52 border-b bg-muted/20">
        <AgentGraph nodeStates={nodeStates} />
      </div>

      {/* Tabs: Evidence | Trace | Raw State */}
      <div className="flex-1 px-6 py-4">
        <Tabs defaultValue="trace">
          <TabsList className="mb-4">
            <TabsTrigger value="trace">
              Trace
              {activeTraces.length > 0 && (
                <Badge variant="secondary" className="ml-2 text-xs">
                  {activeTraces.length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="evidence">
              Evidence
              {activeEvidence.length > 0 && (
                <Badge variant="secondary" className="ml-2 text-xs">
                  {activeEvidence.length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="raw">Raw State</TabsTrigger>
          </TabsList>

          {/* Live stream / trace tab */}
          <TabsContent value="trace" className="mt-0">
            <StatusStream traces={activeTraces} />
          </TabsContent>

          {/* Evidence tab */}
          <TabsContent value="evidence" className="mt-0">
            <EvidencePanel evidence={activeEvidence} />
          </TabsContent>

          {/* Raw state tab */}
          <TabsContent value="raw" className="mt-0">
            <RawStateViewer
              state={activeRawState}
              fallbackVerdict={activeVerdict as unknown as Record<string, unknown>}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
