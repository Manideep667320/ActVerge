// ─── Verdict & Status Types ────────────────────────────────────────────────

export type VerdictType =
  | "SUCCESS"
  | "PARTIAL"
  | "FAILED"
  | "UNCERTAIN"
  | "PENDING";

export type TaskStatus =
  | "queued"
  | "running"
  | "interpreting"
  | "executing"
  | "observing"
  | "collecting_evidence"
  | "verifying"
  | "recovering"
  | "escalated"
  | "complete"
  | "error";

export type NodeState = "idle" | "running" | "complete" | "error";

// ─── Agent Node Names ───────────────────────────────────────────────────────

export type AgentNodeName =
  | "task_interpreter"
  | "executor"
  | "state_observer"
  | "evidence_collector"
  | "outcome_verifier"
  | "recovery_agent"
  | "human_escalation";

// ─── Core Models ────────────────────────────────────────────────────────────

export interface Task {
  id: string;
  user_task: string;
  status: TaskStatus;
  created_at: string;
  updated_at: string;
}

export interface Verdict {
  task_id: string;
  verdict: VerdictType;
  reasoning: string;
  evidence_summary: string[];
  recovery_attempted: boolean;
  escalated: boolean;
  created_at: string;
}

export interface Evidence {
  type: "screenshot" | "dom_diff" | "log" | "network" | "accessibility" | "storage";
  label: string;
  content: string;
  timestamp: string;
}

export interface ActionTrace {
  step: number;
  action: string;
  target?: string;
  value?: string;
  result?: string;
  timestamp: string;
}

export interface RawState {
  task_id: string;
  url?: string;
  dom_snapshot?: string;
  local_storage?: Record<string, string>;
  cookies?: Record<string, string>;
  captured_at: string;
}

// ─── SSE Events ─────────────────────────────────────────────────────────────

export interface SSEEvent {
  type: "node_start" | "node_complete" | "verdict" | "error" | "trace" | "state";
  node?: AgentNodeName;
  data?: unknown;
}

// ─── API Payloads ───────────────────────────────────────────────────────────

export interface CreateTaskPayload {
  user_task: string;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
}
