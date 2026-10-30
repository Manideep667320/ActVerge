"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import {
  Copy,
  Check,
  Code2,
  FileCode,
  ShieldCheck,
  Globe,
  Terminal,
  Activity,
  ChevronDown,
  ChevronRight,
} from "lucide-react";

interface RawStateViewerProps {
  state: Record<string, unknown> | null;
  fallbackVerdict?: Record<string, unknown> | null;
}

export default function RawStateViewer({
  state,
  fallbackVerdict,
}: RawStateViewerProps) {
  const [copied, setCopied] = useState(false);
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({
    spec: true,
    snapshots: true,
    evidence: true,
    json: false,
  });

  const displayData = state ?? fallbackVerdict;

  if (!displayData) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-muted-foreground gap-2">
        <Code2 className="h-8 w-8 opacity-30" />
        <p className="text-sm">No raw state captured yet.</p>
        <p className="text-xs opacity-60">
          State variables from each LangGraph node will be displayed here.
        </p>
      </div>
    );
  }

  const toggleSection = (key: string) => {
    setOpenSections((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const copyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(displayData, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const outcomeSpec = displayData.outcome_spec as Record<string, unknown> | undefined;
  const baselineSnap = displayData.baseline_snapshot as Record<string, unknown> | undefined;
  const postSnap = displayData.post_action_snapshot as Record<string, unknown> | undefined;
  const evidencePkg = displayData.evidence_package as Record<string, unknown> | undefined;
  const trace = (displayData.action_trace as unknown[]) ?? [];
  const risk = String(outcomeSpec?.side_effect_risk ?? "LOW");

  const riskColors: Record<string, string> = {
    LOW: "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950 dark:text-emerald-300",
    MEDIUM: "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950 dark:text-amber-300",
    HIGH: "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950 dark:text-rose-300",
    CRITICAL: "bg-red-100 text-red-800 border-red-300 dark:bg-red-950 dark:text-red-300",
  };

  return (
    <div className="space-y-4">
      {/* Top Banner & Copy Bar */}
      <div className="flex items-center justify-between p-3.5 rounded-lg border bg-card gap-4 flex-wrap">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            <Terminal className="h-4 w-4 text-primary" />
            <span>State Pipeline Inspector</span>
          </div>

          <span className="text-xs px-2 py-0.5 rounded-full font-mono font-medium bg-muted text-muted-foreground">
            {Object.keys(displayData).length} Top-Level Keys
          </span>

          <span
            className={cn(
              "text-xs px-2 py-0.5 rounded-full font-medium border",
              riskColors[risk] ?? "bg-muted text-muted-foreground"
            )}
          >
            Risk: {risk}
          </span>

          {trace.length > 0 && (
            <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-indigo-50 text-indigo-700 border border-indigo-200 dark:bg-indigo-950 dark:text-indigo-300">
              {trace.length} Trace Steps
            </span>
          )}
        </div>

        <button
          onClick={copyJson}
          className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-md border bg-background hover:bg-accent transition-colors shrink-0"
        >
          {copied ? (
            <>
              <Check className="h-3.5 w-3.5 text-emerald-600" />
              <span>Copied JSON</span>
            </>
          ) : (
            <>
              <Copy className="h-3.5 w-3.5" />
              <span>Copy Full State</span>
            </>
          )}
        </button>
      </div>

      {/* 1. Task & Outcome Specification */}
      {outcomeSpec && (
        <div className="rounded-lg border bg-card overflow-hidden">
          <button
            onClick={() => toggleSection("spec")}
            className="w-full px-4 py-2.5 bg-muted/20 border-b flex items-center justify-between text-left hover:bg-muted/30 transition-colors"
          >
            <div className="flex items-center gap-2 text-xs font-semibold">
              <ShieldCheck className="h-4 w-4 text-indigo-500" />
              <span>1. Task &amp; Expected Outcome Specification (Interpreter Output)</span>
            </div>
            {openSections.spec ? (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            )}
          </button>

          {openSections.spec && (
            <div className="p-4 space-y-3 text-xs divide-y divide-border/50">
              <div className="flex items-start gap-4 pt-1">
                <span className="font-mono text-muted-foreground w-36 shrink-0 font-medium">
                  task_description
                </span>
                <span className="font-mono text-foreground/90 font-medium">
                  {String(outcomeSpec.task_description ?? displayData.user_task ?? "")}
                </span>
              </div>

              {outcomeSpec.expected_url_pattern !== undefined && (
                <div className="flex items-start gap-4 pt-2">
                  <span className="font-mono text-muted-foreground w-36 shrink-0 font-medium">
                    expected_url_pattern
                  </span>
                  <code className="bg-muted px-1.5 py-0.5 rounded font-mono">
                    {String(outcomeSpec.expected_url_pattern ?? "null (any validated domain)")}
                  </code>
                </div>
              )}

              {Array.isArray(outcomeSpec.required_dom_elements) && (
                <div className="flex items-start gap-4 pt-2">
                  <span className="font-mono text-muted-foreground w-36 shrink-0 font-medium">
                    required_dom_elements
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {outcomeSpec.required_dom_elements.map((el, i) => (
                      <code key={i} className="bg-muted px-1.5 py-0.5 rounded font-mono text-[11px]">
                        {String(el)}
                      </code>
                    ))}
                  </div>
                </div>
              )}

              {Array.isArray(outcomeSpec.required_text) && (
                <div className="flex items-start gap-4 pt-2">
                  <span className="font-mono text-muted-foreground w-36 shrink-0 font-medium">
                    required_text
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {outcomeSpec.required_text.map((t, i) => (
                      <span
                        key={i}
                        className="bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950 dark:text-emerald-300 px-1.5 py-0.5 rounded font-mono text-[11px]"
                      >
                        ✓ &ldquo;{String(t)}&rdquo;
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {Array.isArray(outcomeSpec.forbidden_text) && (
                <div className="flex items-start gap-4 pt-2">
                  <span className="font-mono text-muted-foreground w-36 shrink-0 font-medium">
                    forbidden_text
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {outcomeSpec.forbidden_text.map((f, i) => (
                      <span
                        key={i}
                        className="bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950 dark:text-rose-300 px-1.5 py-0.5 rounded font-mono text-[11px]"
                      >
                        ✕ &ldquo;{String(f)}&rdquo;
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* 2. Web Snapshots */}
      {(baselineSnap || postSnap) && (
        <div className="rounded-lg border bg-card overflow-hidden">
          <button
            onClick={() => toggleSection("snapshots")}
            className="w-full px-4 py-2.5 bg-muted/20 border-b flex items-center justify-between text-left hover:bg-muted/30 transition-colors"
          >
            <div className="flex items-center gap-2 text-xs font-semibold">
              <Globe className="h-4 w-4 text-sky-500" />
              <span>2. Environment Snapshots (Baseline vs. Post-Action State)</span>
            </div>
            {openSections.snapshots ? (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            )}
          </button>

          {openSections.snapshots && (
            <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="border rounded-md p-3 bg-muted/10 space-y-2">
                <span className="font-semibold text-muted-foreground uppercase text-[10px] tracking-wider">
                  Baseline (Initial Load)
                </span>
                <p className="font-mono truncate">
                  <span className="text-muted-foreground">URL: </span>
                  {String(baselineSnap?.url ?? "about:blank")}
                </p>
                <p className="font-mono text-[11px] text-muted-foreground">
                  Status: {String(baselineSnap?.status ?? "initial")}
                </p>
              </div>

              <div className="border rounded-md p-3 bg-muted/10 space-y-2">
                <span className="font-semibold text-emerald-600 uppercase text-[10px] tracking-wider">
                  Post-Action (Final State)
                </span>
                <p className="font-mono truncate">
                  <span className="text-muted-foreground">URL: </span>
                  {String(postSnap?.url ?? "N/A")}
                </p>
                <p className="font-mono text-[11px] text-muted-foreground">
                  Status: {String(postSnap?.status ?? "success")}
                </p>
                {Boolean(postSnap?.title) && (
                  <p className="font-medium text-foreground/90 truncate">
                    Title: {String(postSnap?.title)}
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 3. Evidence Telemetry Summary */}
      {evidencePkg && (
        <div className="rounded-lg border bg-card overflow-hidden">
          <button
            onClick={() => toggleSection("evidence")}
            className="w-full px-4 py-2.5 bg-muted/20 border-b flex items-center justify-between text-left hover:bg-muted/30 transition-colors"
          >
            <div className="flex items-center gap-2 text-xs font-semibold">
              <Activity className="h-4 w-4 text-emerald-500" />
              <span>3. Multi-Source Evidence Package Summary</span>
            </div>
            {openSections.evidence ? (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            )}
          </button>

          {openSections.evidence && (
            <div className="p-4 grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
              <div className="p-2.5 border rounded-md bg-muted/20">
                <span className="text-[10px] text-muted-foreground uppercase font-semibold">Network Calls</span>
                <p className="text-base font-bold mt-0.5">
                  {Number(evidencePkg.network_requests_count ?? (Array.isArray(evidencePkg.network_logs) ? evidencePkg.network_logs.length : 0))}
                </p>
              </div>

              <div className="p-2.5 border rounded-md bg-muted/20">
                <span className="text-[10px] text-muted-foreground uppercase font-semibold">Console Logs</span>
                <p className="text-base font-bold mt-0.5">
                  {Array.isArray(evidencePkg.console_logs) ? evidencePkg.console_logs.length : 0}
                </p>
              </div>

              <div className="p-2.5 border rounded-md bg-muted/20">
                <span className="text-[10px] text-muted-foreground uppercase font-semibold">Visual Proof</span>
                <p className="text-base font-bold text-emerald-600 mt-0.5">
                  {evidencePkg.screenshot_url ? "Captured" : "None"}
                </p>
              </div>

              <div className="p-2.5 border rounded-md bg-muted/20">
                <span className="text-[10px] text-muted-foreground uppercase font-semibold">Verified Tokens</span>
                <p className="text-base font-bold mt-0.5">
                  {Array.isArray(evidencePkg.confirmation_tokens) ? evidencePkg.confirmation_tokens.length : 0}
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 4. Full Raw State JSON Tree */}
      <div className="rounded-lg border bg-card overflow-hidden">
        <button
          onClick={() => toggleSection("json")}
          className="w-full px-4 py-2.5 bg-muted/20 border-b flex items-center justify-between text-left hover:bg-muted/30 transition-colors"
        >
          <div className="flex items-center gap-2 text-xs font-semibold">
            <FileCode className="h-4 w-4 text-muted-foreground" />
            <span>4. Complete LangGraph Execution State (Raw JSON Tree)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-muted-foreground font-mono">
              {openSections.json ? "Collapse" : "Expand"}
            </span>
            {openSections.json ? (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            )}
          </div>
        </button>

        {openSections.json && (
          <div className="p-4 bg-muted/10 overflow-auto max-h-[60vh]">
            <pre className="text-xs font-mono whitespace-pre-wrap break-all leading-relaxed text-foreground/90">
              {JSON.stringify(displayData, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
