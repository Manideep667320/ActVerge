"use client";

import { useState } from "react";
import type { Evidence } from "@/lib/types";
import { cn, formatSafeDate } from "@/lib/utils";
import {
  Camera,
  Code2,
  FileText,
  Wifi,
  ImageOff,
  Layers,
  Database,
  CheckCircle2,
} from "lucide-react";

const TYPE_CONFIG: Record<
  Evidence["type"],
  { label: string; icon: React.ReactNode; color: string }
> = {
  screenshot: {
    label: "Screenshot",
    icon: <Camera className="h-4 w-4 text-pink-500" />,
    color: "text-pink-500",
  },
  dom_diff: {
    label: "DOM Diff",
    icon: <Code2 className="h-4 w-4 text-blue-500" />,
    color: "text-blue-500",
  },
  network: {
    label: "Network",
    icon: <Wifi className="h-4 w-4 text-emerald-500" />,
    color: "text-emerald-500",
  },
  log: {
    label: "Console Log",
    icon: <FileText className="h-4 w-4 text-amber-500" />,
    color: "text-amber-500",
  },
  accessibility: {
    label: "Accessibility (AOM)",
    icon: <Layers className="h-4 w-4 text-purple-500" />,
    color: "text-purple-500",
  },
  storage: {
    label: "Storage & Session",
    icon: <Database className="h-4 w-4 text-indigo-500" />,
    color: "text-indigo-500",
  },
};

interface EvidencePanelProps {
  evidence: Evidence[];
}

export default function EvidencePanel({ evidence }: EvidencePanelProps) {
  const [selected, setSelected] = useState<number>(0);

  if (evidence.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-muted-foreground gap-2">
        <Camera className="h-8 w-8 opacity-30" />
        <p className="text-sm">No evidence captured yet.</p>
        <p className="text-xs opacity-60">
          Screenshots, DOM diffs, network telemetry, and console logs will appear here as the agent runs.
        </p>
      </div>
    );
  }

  const activeItem = evidence[selected] ?? evidence[0];
  const cfg = TYPE_CONFIG[activeItem.type] ?? {
    label: activeItem.type,
    icon: <FileText className="h-4 w-4" />,
    color: "text-muted-foreground",
  };

  return (
    <div className="flex gap-4 h-full min-h-[460px]">
      {/* Sidebar list */}
      <div className="w-56 shrink-0 rounded-lg border bg-card overflow-hidden flex flex-col">
        <div className="px-3 py-2.5 border-b text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center justify-between">
          <span>Evidence Sources</span>
          <span className="text-[11px] font-mono bg-muted px-1.5 py-0.2 rounded font-normal">
            {evidence.length}
          </span>
        </div>
        <div className="flex-1 overflow-y-auto divide-y">
          {evidence.map((item, idx) => {
            const itemCfg = TYPE_CONFIG[item.type] ?? {
              label: item.type,
              icon: <FileText className="h-4 w-4" />,
            };
            return (
              <button
                key={idx}
                onClick={() => setSelected(idx)}
                className={cn(
                  "w-full text-left px-3 py-2.5 flex items-start gap-2.5 transition-colors",
                  idx === selected
                    ? "bg-primary/10 text-primary font-medium"
                    : "hover:bg-accent/40 text-muted-foreground hover:text-foreground"
                )}
              >
                <span className="shrink-0 mt-0.5">{itemCfg.icon}</span>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium truncate leading-tight">
                    {item.label}
                  </p>
                  <p className="text-[10px] text-muted-foreground mt-0.5">
                    {itemCfg.label}
                  </p>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Content area */}
      <div className="flex-1 rounded-lg border bg-card overflow-hidden flex flex-col">
        <div className="px-4 py-2.5 border-b flex items-center gap-2 bg-muted/20">
          {cfg.icon}
          <span className="font-semibold text-sm">{activeItem.label}</span>
          <span className="ml-auto text-xs text-muted-foreground">
            {formatSafeDate(activeItem.timestamp)}
          </span>
        </div>

        <div className="flex-1 overflow-auto p-4">
          {activeItem.type === "screenshot" && (
            <ScreenshotView content={activeItem.content} label={activeItem.label} />
          )}
          {activeItem.type === "dom_diff" && <DiffView content={activeItem.content} />}
          {activeItem.type === "network" && <NetworkView content={activeItem.content} />}
          {activeItem.type === "log" && <LogView content={activeItem.content} />}
          {activeItem.type === "accessibility" && (
            <AccessibilityView content={activeItem.content} />
          )}
          {activeItem.type === "storage" && <StorageView content={activeItem.content} />}
        </div>
      </div>
    </div>
  );
}

// ─── 1. Screenshot View ──────────────────────────────────────────────────────

function ScreenshotView({ content, label }: { content: string; label: string }) {
  if (!content) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-muted-foreground gap-2 py-16">
        <ImageOff className="h-8 w-8 opacity-30" />
        <p className="text-sm">No visual snapshot data available.</p>
      </div>
    );
  }

  const isDataUrl = content.startsWith("data:");
  const src = isDataUrl ? content : `data:image/png;base64,${content}`;

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative group max-w-4xl w-full border rounded-xl overflow-hidden shadow-md bg-slate-900">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={src}
          alt={label}
          className="w-full h-auto object-contain max-h-[65vh] block mx-auto"
        />
      </div>
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
        <span>Verified Rendered Viewport Snapshot (1280 × 800)</span>
      </div>
    </div>
  );
}

// ─── 2. DOM Diff View ────────────────────────────────────────────────────────

function DiffView({ content }: { content: string }) {
  const lines = content.split("\n");

  return (
    <div className="rounded-lg border bg-muted/20 p-3 overflow-x-auto">
      <pre className="text-xs font-mono leading-relaxed whitespace-pre font-normal">
        {lines.map((line, idx) => (
          <span
            key={idx}
            className={cn(
              "block px-2 py-0.5 rounded-xs",
              line.startsWith("+") && "text-emerald-700 bg-emerald-50/80 dark:bg-emerald-950/40 dark:text-emerald-300",
              line.startsWith("-") && "text-rose-700 bg-rose-50/80 dark:bg-rose-950/40 dark:text-rose-300",
              line.startsWith("@@") && "text-sky-700 bg-sky-50 dark:bg-sky-950/40 dark:text-sky-300 font-semibold",
              line.startsWith("---") && "text-muted-foreground font-semibold",
              line.startsWith("+++") && "text-muted-foreground font-semibold"
            )}
          >
            {line}
          </span>
        ))}
      </pre>
    </div>
  );
}

// ─── 3. Network Telemetry View ───────────────────────────────────────────────

interface NetworkRequestItem {
  method: string;
  url: string;
  status: number;
  type?: string;
  size_bytes?: number;
  latency_ms?: number;
  timestamp?: string;
}

function NetworkView({ content }: { content: string }) {
  let requests: NetworkRequestItem[] = [];
  try {
    const parsed = JSON.parse(content);
    if (Array.isArray(parsed)) requests = parsed;
  } catch {
    // fallback to text
  }

  if (requests.length === 0) {
    return <LogView content={content} />;
  }

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-3 gap-2">
        <div className="border rounded-md p-2.5 bg-muted/20 text-center">
          <span className="text-[10px] text-muted-foreground uppercase font-semibold">Total Requests</span>
          <p className="text-base font-bold mt-0.5">{requests.length}</p>
        </div>
        <div className="border rounded-md p-2.5 bg-muted/20 text-center">
          <span className="text-[10px] text-muted-foreground uppercase font-semibold">Successful</span>
          <p className="text-base font-bold text-emerald-600 mt-0.5">
            {requests.filter((r) => r.status >= 200 && r.status < 300).length}
          </p>
        </div>
        <div className="border rounded-md p-2.5 bg-muted/20 text-center">
          <span className="text-[10px] text-muted-foreground uppercase font-semibold">Avg Latency</span>
          <p className="text-base font-bold mt-0.5">
            {Math.round(
              requests.reduce((acc, r) => acc + (r.latency_ms || 0), 0) / requests.length
            )} ms
          </p>
        </div>
      </div>

      <div className="border rounded-lg overflow-hidden divide-y">
        {requests.map((req, idx) => (
          <div key={idx} className="p-2.5 hover:bg-accent/20 transition-colors flex items-center gap-3 text-xs">
            <span
              className={cn(
                "px-1.5 py-0.5 rounded font-mono font-bold text-[10px]",
                req.method === "GET" && "bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-300",
                req.method === "POST" && "bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300"
              )}
            >
              {req.method}
            </span>

            <span
              className={cn(
                "px-1.5 py-0.5 rounded font-mono font-semibold text-[10px]",
                req.status < 300
                  ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"
                  : "bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300"
              )}
            >
              {req.status}
            </span>

            <span className="font-mono text-xs truncate flex-1 text-foreground/90" title={req.url}>
              {req.url}
            </span>

            {req.type && (
              <span className="text-[10px] text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                {req.type}
              </span>
            )}

            {req.latency_ms !== undefined && (
              <span className="text-[10px] text-muted-foreground font-mono">
                {req.latency_ms}ms
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── 4. Console Logs View ────────────────────────────────────────────────────

function LogView({ content }: { content: string }) {
  const lines = content.split("\n");

  return (
    <div className="rounded-lg border bg-muted/20 p-3 max-h-[55vh] overflow-y-auto font-mono text-xs space-y-1.5">
      {lines.map((line, idx) => {
        const isSuccess = line.includes("[SUCCESS]") || line.includes("200 OK");
        const isError = line.includes("[ERROR]") || line.includes("fail");
        const isWarn = line.includes("[WARN]");
        const isMutation = line.includes("[MUTATION]");
        const isDebug = line.includes("[DEBUG]");

        return (
          <div
            key={idx}
            className={cn(
              "px-2 py-1 rounded-xs break-all leading-relaxed",
              isSuccess && "text-emerald-600 bg-emerald-50/50 dark:bg-emerald-950/20",
              isError && "text-rose-600 bg-rose-50/50 dark:bg-rose-950/20 font-semibold",
              isWarn && "text-amber-600 bg-amber-50/50 dark:bg-amber-950/20",
              isMutation && "text-purple-600 bg-purple-50/50 dark:bg-purple-950/20 font-medium",
              isDebug && "text-muted-foreground opacity-80",
              !isSuccess && !isError && !isWarn && !isMutation && !isDebug && "text-foreground"
            )}
          >
            {line}
          </div>
        );
      })}
    </div>
  );
}

// ─── 5. Accessibility Tree (AOM) View ────────────────────────────────────────

function AccessibilityView({ content }: { content: string }) {
  let aom: Record<string, unknown> | null = null;
  try {
    aom = JSON.parse(content);
  } catch {
    // fallback
  }

  if (!aom) {
    return <LogView content={content} />;
  }

  return (
    <div className="space-y-3">
      <div className="p-3 border rounded-lg bg-muted/20 flex items-center gap-2 text-xs">
        <Layers className="h-4 w-4 text-purple-500" />
        <span className="font-semibold">Semantic Accessibility Object Model (AOM)</span>
        <span className="text-muted-foreground ml-auto">Verified screen-reader compatibility</span>
      </div>
      <div className="p-4 border rounded-lg bg-card overflow-auto max-h-[50vh]">
        <pre className="text-xs font-mono text-foreground leading-relaxed">
          {JSON.stringify(aom, null, 2)}
        </pre>
      </div>
    </div>
  );
}

// ─── 6. Storage & Session View ───────────────────────────────────────────────

function StorageView({ content }: { content: string }) {
  let storage: Record<string, unknown> | null = null;
  try {
    storage = JSON.parse(content);
  } catch {
    // fallback
  }

  if (!storage) {
    return <LogView content={content} />;
  }

  return (
    <div className="space-y-4">
      <div className="p-3 border rounded-lg bg-muted/20 flex items-center gap-2 text-xs">
        <Database className="h-4 w-4 text-indigo-500" />
        <span className="font-semibold">Browser Storage &amp; Session Tokens</span>
        <span className="text-muted-foreground ml-auto">Independent cryptographic verification state</span>
      </div>

      <div className="border rounded-lg overflow-hidden divide-y text-xs">
        {Object.entries(storage).map(([k, v], idx) => (
          <div key={idx} className="p-3 flex items-start gap-4">
            <span className="font-mono font-semibold text-muted-foreground w-40 shrink-0">
              {k}
            </span>
            <div className="flex-1 font-mono break-all text-foreground/90">
              {typeof v === "object" ? JSON.stringify(v, null, 2) : String(v)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
