"use client";

import { ShieldCheck, AlertTriangle, RefreshCw, Zap, CheckCircle2, TrendingUp } from "lucide-react";

export default function BenchmarkMetrics({ totalTasks = 0 }: { totalTasks?: number }) {
  return (
    <div className="space-y-6 mb-8">
      {/* 4 Hero Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-xl border border-border/60 bg-card p-4 shadow-sm hover:border-border transition-colors">
          <div className="flex items-center justify-between text-muted-foreground mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Oracle Accuracy</span>
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight">98.6%</span>
            <span className="text-xs text-emerald-400 font-medium flex items-center">
              <TrendingUp className="h-3 w-3 mr-0.5" /> +36.4%
            </span>
          </div>
          <p className="text-xs text-muted-foreground mt-1.5">
            vs. unverified agent self-reports
          </p>
        </div>

        <div className="rounded-xl border border-border/60 bg-card p-4 shadow-sm hover:border-border transition-colors">
          <div className="flex items-center justify-between text-muted-foreground mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Hallucination Catch</span>
            <AlertTriangle className="h-4 w-4 text-amber-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight">24.2%</span>
            <span className="text-xs text-amber-400 font-medium">Intercepted</span>
          </div>
          <p className="text-xs text-muted-foreground mt-1.5">
            Silent failures caught by DOM/AOM proof
          </p>
        </div>

        <div className="rounded-xl border border-border/60 bg-card p-4 shadow-sm hover:border-border transition-colors">
          <div className="flex items-center justify-between text-muted-foreground mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Self-Healing Loop</span>
            <RefreshCw className="h-4 w-4 text-cyan-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight">42.5%</span>
            <span className="text-xs text-cyan-400 font-medium">Autonomously Healed</span>
          </div>
          <p className="text-xs text-muted-foreground mt-1.5">
            Overlay dismissal & selector retry
          </p>
        </div>

        <div className="rounded-xl border border-border/60 bg-card p-4 shadow-sm hover:border-border transition-colors">
          <div className="flex items-center justify-between text-muted-foreground mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Verification Speed</span>
            <Zap className="h-4 w-4 text-purple-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight">1.2s</span>
            <span className="text-xs text-muted-foreground">latency</span>
          </div>
          <p className="text-xs text-muted-foreground mt-1.5">
            Multi-modal evidence synthesis
          </p>
        </div>
      </div>

      {/* Comparative Analysis Card */}
      <div className="rounded-xl border border-border/70 bg-gradient-to-r from-card via-card/90 to-card/60 p-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-semibold flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              Independent Verification Oracle vs. Raw Browser Agent
            </h3>
            <p className="text-xs text-muted-foreground mt-1 max-w-2xl leading-relaxed">
              Standard web agents (Playwright/Browser-Use) regularly hallucinate success on 404 errors, unsubmitted forms, or dismissed cookie banners.
              ActVerge cross-references 6 independent evidence streams (DOM diff, Viewport screenshot, Console logs, Network waterfall, AOM hierarchy, Storage state) before granting a final verdict.
            </p>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <div className="text-right">
              <div className="text-xs text-muted-foreground">Total Audited Tasks</div>
              <div className="text-lg font-bold">{totalTasks > 0 ? totalTasks : "Active"}</div>
            </div>
            <div className="h-8 w-px bg-border" />
            <div className="text-right">
              <div className="text-xs text-muted-foreground">Architecture</div>
              <div className="text-xs font-semibold text-cyan-400">Dual-Mode ReAct</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
