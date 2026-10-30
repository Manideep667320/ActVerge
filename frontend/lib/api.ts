import type {
  Task,
  TaskListResponse,
  CreateTaskPayload,
  Verdict,
  Evidence,
  ActionTrace,
} from "./types";

const BASE = "/api";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });

  if (!res.ok) {
    let message = `API error ${res.status}: ${res.statusText}`;
    try {
      const body = await res.json();
      message = body?.detail ?? body?.message ?? message;
    } catch {
      // ignore
    }
    throw new Error(message);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

/** Submit a new task */
export async function createTask(payload: CreateTaskPayload): Promise<Task> {
  return apiFetch<Task>("/tasks", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/** List all tasks */
export async function fetchTasks(
  limit = 50,
  offset = 0
): Promise<TaskListResponse> {
  return apiFetch<TaskListResponse>(
    `/tasks?limit=${limit}&offset=${offset}`
  );
}

/** Get a single task */
export async function fetchTask(id: string): Promise<Task> {
  return apiFetch<Task>(`/tasks/${id}`);
}

/** Delete a task */
export async function deleteTask(id: string): Promise<void> {
  return apiFetch<void>(`/tasks/${id}`, { method: "DELETE" });
}

/** Fetch verdict for a completed task */
export async function fetchVerdict(taskId: string): Promise<Verdict> {
  return apiFetch<Verdict>(`/tasks/${taskId}/verdict`);
}

/** Fetch evidence list */
export async function fetchEvidence(taskId: string): Promise<Evidence[]> {
  return apiFetch<Evidence[]>(`/tasks/${taskId}/evidence`);
}

/** Fetch action trace */
export async function fetchTrace(taskId: string): Promise<ActionTrace[]> {
  return apiFetch<ActionTrace[]>(`/tasks/${taskId}/trace`);
}

/** Fetch complete execution raw state */
export async function fetchTaskState(taskId: string): Promise<Record<string, unknown>> {
  return apiFetch<Record<string, unknown>>(`/tasks/${taskId}/state`);
}

/** Returns the SSE stream URL for a given task */
export function getStreamUrl(taskId: string): string {
  return `${BASE}/tasks/${taskId}/stream`;
}
