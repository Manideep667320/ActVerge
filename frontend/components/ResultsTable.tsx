"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchTasks, fetchVerdict, deleteTask } from "@/lib/api";
import { useActVergeStore } from "@/lib/store";
import type { Task, Verdict } from "@/lib/types";
import VerdictBadge from "./VerdictBadge";
import {
  Loader2,
  Trash2,
  ArrowRight,
  RefreshCw,
  AlertCircle,
} from "lucide-react";
import { toast } from "sonner";
import { cn, formatSafeDate } from "@/lib/utils";

const STATUS_CELL: Record<string, string> = {
  complete: "text-green-600",
  error: "text-red-500",
  escalated: "text-red-500",
  running: "text-blue-500",
  queued: "text-muted-foreground",
};

export default function ResultsTable() {
  const { tasks, tasksFetched, setTasks } = useActVergeStore();
  const [verdicts, setVerdicts] = useState<Record<string, Verdict>>({});
  const [loading, setLoading] = useState(!tasksFetched);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchTasks(50, 0);
      setTasks(res.tasks);

      // Fetch verdicts for completed tasks
      const completedTasks = res.tasks.filter((t) => t.status === "complete");
      const verdictResults = await Promise.allSettled(
        completedTasks.map((t) => fetchVerdict(t.id))
      );
      const newVerdicts: Record<string, Verdict> = {};
      verdictResults.forEach((r, i) => {
        if (r.status === "fulfilled") {
          newVerdicts[completedTasks[i].id] = r.value;
        }
      });
      setVerdicts(newVerdicts);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleDelete(task: Task) {
    setDeleting(task.id);
    try {
      await deleteTask(task.id);
      setTasks(tasks.filter((t) => t.id !== task.id));
      toast.success("Task deleted");
    } catch (err) {
      toast.error("Delete failed", {
        description: err instanceof Error ? err.message : "Unknown error",
      });
    } finally {
      setDeleting(null);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16 gap-2 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" />
        Loading tasks…
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-3 text-muted-foreground">
        <AlertCircle className="h-8 w-8 text-red-400" />
        <p className="text-sm">{error}</p>
        <button
          onClick={load}
          className="text-sm text-primary hover:underline flex items-center gap-1"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Retry
        </button>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-16 text-muted-foreground">
        <p className="text-sm">No tasks yet.</p>
        <Link href="/" className="text-sm text-primary hover:underline mt-2 inline-block">
          Submit your first task →
        </Link>
      </div>
    );
  }

  return (
    <div className="rounded-xl border overflow-hidden">
      {/* Table header row */}
      <div className="flex items-center justify-between px-5 py-3 border-b bg-card">
        <span className="text-sm font-semibold">
          {tasks.length} task{tasks.length !== 1 ? "s" : ""}
        </span>
        <button
          onClick={load}
          className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Refresh
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/40 text-xs text-muted-foreground uppercase tracking-wide">
              <th className="text-left px-5 py-2.5 font-medium">Task</th>
              <th className="text-left px-4 py-2.5 font-medium w-32">Status</th>
              <th className="text-left px-4 py-2.5 font-medium w-28">Verdict</th>
              <th className="text-left px-4 py-2.5 font-medium w-40">Created</th>
              <th className="px-4 py-2.5 w-24" />
            </tr>
          </thead>
          <tbody className="divide-y">
            {tasks.map((task) => {
              const verdict = verdicts[task.id];
              return (
                <tr
                  key={task.id}
                  className="hover:bg-accent/30 transition-colors group"
                >
                  {/* Task description */}
                  <td className="px-5 py-3 max-w-xs">
                    <p className="truncate font-medium">{task.user_task}</p>
                    <p className="text-xs text-muted-foreground font-mono mt-0.5 truncate">
                      {task.id}
                    </p>
                  </td>

                  {/* Status */}
                  <td className="px-4 py-3">
                    <span
                      className={cn(
                        "text-xs font-medium capitalize",
                        STATUS_CELL[task.status] ?? "text-muted-foreground"
                      )}
                    >
                      {task.status.replace(/_/g, " ")}
                    </span>
                  </td>

                  {/* Verdict */}
                  <td className="px-4 py-3">
                    {verdict ? (
                      <VerdictBadge verdict={verdict.verdict} size="sm" />
                    ) : task.status === "complete" ? (
                      <span className="text-xs text-muted-foreground">—</span>
                    ) : (
                      <span className="text-xs text-muted-foreground">Pending</span>
                    )}
                  </td>

                  {/* Created at */}
                  <td className="px-4 py-3 text-xs text-muted-foreground">
                    {formatSafeDate(task.created_at)}
                  </td>

                  {/* Actions */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2 justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                      <Link
                        href={`/tasks/${task.id}`}
                        className="p-1 rounded hover:bg-accent text-muted-foreground hover:text-primary transition-colors"
                        title="View task"
                      >
                        <ArrowRight className="h-4 w-4" />
                      </Link>
                      <button
                        onClick={() => handleDelete(task)}
                        disabled={deleting === task.id}
                        className="p-1 rounded hover:bg-red-50 dark:hover:bg-red-950/40 text-muted-foreground hover:text-red-500 transition-colors disabled:opacity-40"
                        title="Delete task"
                      >
                        {deleting === task.id ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Trash2 className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
