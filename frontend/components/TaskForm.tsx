"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { createTask } from "@/lib/api";
import { useActVergeStore } from "@/lib/store";
import { Loader2, Send } from "lucide-react";

const EXAMPLE_TASKS = [
  "Go to amazon.com and add the first result for 'mechanical keyboard' to the cart",
  "Fill out the contact form on example.com with name 'Test User' and email 'test@test.com'",
  "Search Google for 'best coffee shops in NYC' and summarize the top 3 results",
];

export default function TaskForm() {
  const [task, setTask] = useState("");
  const [isPending, startTransition] = useTransition();
  const router = useRouter();
  const { addTask, resetNodeStates } = useActVergeStore();

  const canSubmit = task.trim().length > 0 && !isPending;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;

    startTransition(async () => {
      try {
        resetNodeStates();
        const newTask = await createTask({ user_task: task.trim() });
        addTask(newTask);
        toast.success("Task submitted!", {
          description: `Task ID: ${newTask.id}`,
        });
        setTask("");
        router.push(`/tasks/${newTask.id}`);
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Failed to submit task";
        toast.error("Submission failed", { description: msg });
      }
    });
  }

  return (
    <div className="rounded-xl border bg-card shadow-sm p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <label
            htmlFor="task-input"
            className="text-sm font-medium text-foreground"
          >
            Describe what you want the agent to do
          </label>
          <textarea
            id="task-input"
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder="e.g. Go to amazon.com and add the first result for 'wireless mouse' to the cart…"
            rows={4}
            className="w-full rounded-lg border bg-background px-4 py-3 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring resize-none transition-shadow"
            disabled={isPending}
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                handleSubmit(e as unknown as React.FormEvent);
              }
            }}
          />
          <p className="text-xs text-muted-foreground">
            Press{" "}
            <kbd className="rounded border px-1 py-0.5 text-xs font-mono bg-muted">
              ⌘ Enter
            </kbd>{" "}
            to submit
          </p>
        </div>

        <button
          type="submit"
          disabled={!canSubmit}
          className="w-full flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isPending ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Submitting…
            </>
          ) : (
            <>
              <Send className="h-4 w-4" />
              Run Task
            </>
          )}
        </button>
      </form>

      {/* Example tasks */}
      <div className="mt-5 pt-5 border-t">
        <p className="text-xs font-medium text-muted-foreground mb-3">
          Try an example:
        </p>
        <div className="space-y-2">
          {EXAMPLE_TASKS.map((example) => (
            <button
              key={example}
              type="button"
              onClick={() => setTask(example)}
              className="w-full text-left text-xs px-3 py-2 rounded-md border hover:bg-accent hover:text-accent-foreground transition-colors text-muted-foreground"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
