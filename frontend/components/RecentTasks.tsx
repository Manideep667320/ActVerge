"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useActVergeStore } from "@/lib/store";
import { fetchTasks } from "@/lib/api";
import { formatSafeDistance } from "@/lib/utils";
import { ArrowRight, Clock, CheckCircle2, XCircle, Loader2, AlertCircle } from "lucide-react";
import type { TaskStatus } from "@/lib/types";

const statusIcon: Record<TaskStatus, React.ReactNode> = {
  queued: <Clock className="h-4 w-4 text-gray-400" />,
  running: <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />,
  interpreting: <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />,
  executing: <Loader2 className="h-4 w-4 text-indigo-500 animate-spin" />,
  observing: <Loader2 className="h-4 w-4 text-purple-500 animate-spin" />,
  collecting_evidence: <Loader2 className="h-4 w-4 text-amber-500 animate-spin" />,
  verifying: <Loader2 className="h-4 w-4 text-cyan-500 animate-spin" />,
  recovering: <Loader2 className="h-4 w-4 text-orange-500 animate-spin" />,
  escalated: <AlertCircle className="h-4 w-4 text-red-500" />,
  complete: <CheckCircle2 className="h-4 w-4 text-green-500" />,
  error: <XCircle className="h-4 w-4 text-red-500" />,
};

export default function RecentTasks() {
  const { tasks, tasksFetched, setTasks } = useActVergeStore();

  useEffect(() => {
    if (tasksFetched) return;
    fetchTasks(10, 0)
      .then((res) => setTasks(res.tasks))
      .catch(() => setTasks([]));
  }, [tasksFetched, setTasks]);

  if (!tasksFetched) {
    return (
      <div className="text-center py-6 text-sm text-muted-foreground flex items-center justify-center gap-2">
        <Loader2 className="h-4 w-4 animate-spin" />
        Loading recent tasks…
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-6 text-sm text-muted-foreground">
        No tasks yet. Submit your first task above!
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-card shadow-sm overflow-hidden">
      <div className="px-5 py-3 border-b flex items-center justify-between">
        <h2 className="text-sm font-semibold">Recent Tasks</h2>
        <Link
          href="/results"
          className="text-xs text-primary hover:underline flex items-center gap-1"
        >
          View all <ArrowRight className="h-3 w-3" />
        </Link>
      </div>
      <ul className="divide-y">
        {tasks.slice(0, 8).map((task) => (
          <li key={task.id}>
            <Link
              href={`/tasks/${task.id}`}
              className="flex items-center gap-3 px-5 py-3.5 hover:bg-accent/50 transition-colors group"
            >
              <span className="shrink-0">
                {statusIcon[task.status] ?? <Clock className="h-4 w-4 text-gray-400" />}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-sm truncate font-medium group-hover:text-primary transition-colors">
                  {task.user_task}
                </p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {formatSafeDistance(task.created_at)}
                </p>
              </div>
              <ArrowRight className="h-4 w-4 text-muted-foreground shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
