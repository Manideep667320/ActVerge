"use client";

import { useEffect, useRef } from "react";
import type { ActionTrace } from "@/lib/types";
import { cn, formatSafeDistance } from "@/lib/utils";
import {
  MousePointer2,
  Type,
  Navigation,
  RotateCcw,
  Eye,
  MoreHorizontal,
  CheckCircle2,
  XCircle,
  Keyboard,
  ListFilter,
  Hand,
  Clock,
  Camera,
  Upload,
  Move,
} from "lucide-react";

const ACTION_ICONS: Record<string, React.ReactNode> = {
  click: <MousePointer2 className="h-3.5 w-3.5 text-indigo-500" />,
  type: <Type className="h-3.5 w-3.5 text-blue-500" />,
  fill: <Type className="h-3.5 w-3.5 text-blue-500" />,
  navigate: <Navigation className="h-3.5 w-3.5 text-sky-500" />,
  scroll: <RotateCcw className="h-3.5 w-3.5 text-amber-500" />,
  observe: <Eye className="h-3.5 w-3.5 text-emerald-500" />,
  press_key: <Keyboard className="h-3.5 w-3.5 text-purple-500" />,
  key_press: <Keyboard className="h-3.5 w-3.5 text-purple-500" />,
  select: <ListFilter className="h-3.5 w-3.5 text-violet-500" />,
  hover: <Hand className="h-3.5 w-3.5 text-orange-500" />,
  wait: <Clock className="h-3.5 w-3.5 text-cyan-500" />,
  screenshot: <Camera className="h-3.5 w-3.5 text-pink-500" />,
  upload: <Upload className="h-3.5 w-3.5 text-teal-500" />,
  drag: <Move className="h-3.5 w-3.5 text-rose-500" />,
};

const ACTION_BADGE_COLORS: Record<string, string> = {
  navigate: "bg-sky-50 text-sky-700 border-sky-200 dark:bg-sky-950/40 dark:text-sky-300",
  fill: "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300",
  type: "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300",
  press_key: "bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950/40 dark:text-purple-300",
  key_press: "bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950/40 dark:text-purple-300",
  click: "bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300",
  select: "bg-violet-50 text-violet-700 border-violet-200 dark:bg-violet-950/40 dark:text-violet-300",
  hover: "bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-950/40 dark:text-orange-300",
  scroll: "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300",
  wait: "bg-cyan-50 text-cyan-700 border-cyan-200 dark:bg-cyan-950/40 dark:text-cyan-300",
  observe: "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300",
  screenshot: "bg-pink-50 text-pink-700 border-pink-200 dark:bg-pink-950/40 dark:text-pink-300",
};

interface StatusStreamProps {
  traces: ActionTrace[];
}

export default function StatusStream({ traces }: StatusStreamProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to newest entry
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [traces.length]);

  if (traces.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-muted-foreground gap-2">
        <Eye className="h-8 w-8 opacity-30" />
        <p className="text-sm">Waiting for agent actions…</p>
        <p className="text-xs opacity-60">
          Events will appear here as the agent executes the task.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border bg-muted/20 overflow-hidden">
      <div className="px-4 py-2.5 border-b bg-card flex items-center justify-between">
        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
          Action Trace
        </span>
        <span className="text-xs text-muted-foreground">
          {traces.length} step{traces.length !== 1 ? "s" : ""}
        </span>
      </div>

      <div className="max-h-[50vh] overflow-y-auto divide-y">
        {traces.map((trace) => (
          <TraceRow key={trace.step} trace={trace} />
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}

function TraceRow({ trace }: { trace: ActionTrace }) {
  const normAction = trace.action.toLowerCase().replace(/\s+/g, "_");
  const icon =
    ACTION_ICONS[normAction] ?? (
      <MoreHorizontal className="h-3.5 w-3.5 text-muted-foreground" />
    );

  const badgeColor =
    ACTION_BADGE_COLORS[normAction] ??
    "bg-muted text-muted-foreground border-border";

  const succeeded =
    trace.result &&
    !trace.result.toLowerCase().includes("fail") &&
    !trace.result.toLowerCase().includes("error");

  const failed =
    trace.result &&
    (trace.result.toLowerCase().includes("fail") ||
      trace.result.toLowerCase().includes("error"));

  const isKeyAction = normAction === "press_key" || normAction === "key_press";

  return (
    <div className="flex items-start gap-3 px-4 py-3 hover:bg-accent/30 transition-colors">
      {/* Step number */}
      <span className="text-[10px] font-mono text-muted-foreground w-6 shrink-0 pt-0.5 text-right">
        {trace.step}
      </span>

      {/* Action icon */}
      <span className="shrink-0 mt-0.5">{icon}</span>

      {/* Details */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span
            className={cn(
              "text-[11px] font-semibold px-2 py-0.5 rounded border uppercase tracking-wider",
              badgeColor
            )}
          >
            {trace.action.replace(/_/g, " ")}
          </span>

          {trace.target && (
            <code className="text-xs bg-muted px-1.5 py-0.5 rounded font-mono truncate max-w-sm text-foreground/80">
              {trace.target}
            </code>
          )}

          {trace.value && (
            isKeyAction ? (
              <kbd className="text-[11px] font-mono font-semibold px-1.5 py-0.5 bg-muted border border-border rounded shadow-xs">
                {trace.value}
              </kbd>
            ) : (
              <span className="text-xs text-muted-foreground truncate max-w-xs font-medium">
                → &ldquo;{trace.value}&rdquo;
              </span>
            )
          )}
        </div>

        {trace.result && (
          <div
            className={cn(
              "flex items-center gap-1.5 mt-1.5 text-xs font-medium",
              succeeded && "text-emerald-600 dark:text-emerald-400",
              failed && "text-rose-600 dark:text-rose-400",
              !succeeded && !failed && "text-muted-foreground"
            )}
          >
            {succeeded && <CheckCircle2 className="h-3 w-3 shrink-0" />}
            {failed && <XCircle className="h-3 w-3 shrink-0" />}
            <span>{trace.result}</span>
          </div>
        )}
      </div>

      {/* Timestamp */}
      <span className="text-[10px] text-muted-foreground shrink-0 pt-0.5">
        {formatSafeDistance(trace.timestamp)}
      </span>
    </div>
  );
}
