"use client";

import { useCallback, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  Handle,
  Position,
  type NodeTypes,
  type Node,
  type Edge,
  BackgroundVariant,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { cn } from "@/lib/utils";
import type { AgentNodeName, NodeState } from "@/lib/types";
import {
  BrainCircuit,
  Play,
  Eye,
  Camera,
  ShieldCheck,
  RefreshCw,
  UserCog,
} from "lucide-react";

// ─── Node config ──────────────────────────────────────────────────────────────

interface AgentNodeConfig {
  id: AgentNodeName;
  label: string;
  icon: React.ReactNode;
  description: string;
}

const NODE_CONFIGS: AgentNodeConfig[] = [
  {
    id: "task_interpreter",
    label: "Task Interpreter",
    icon: <BrainCircuit className="h-5 w-5" />,
    description: "Parses & plans the task",
  },
  {
    id: "executor",
    label: "Executor",
    icon: <Play className="h-5 w-5" />,
    description: "Runs browser actions",
  },
  {
    id: "state_observer",
    label: "State Observer",
    icon: <Eye className="h-5 w-5" />,
    description: "Reads page state",
  },
  {
    id: "evidence_collector",
    label: "Evidence Collector",
    icon: <Camera className="h-5 w-5" />,
    description: "Captures screenshots & DOM",
  },
  {
    id: "outcome_verifier",
    label: "Outcome Verifier",
    icon: <ShieldCheck className="h-5 w-5" />,
    description: "Validates the result",
  },
  {
    id: "recovery_agent",
    label: "Recovery Agent",
    icon: <RefreshCw className="h-5 w-5" />,
    description: "Retries failed steps",
  },
  {
    id: "human_escalation",
    label: "Human Escalation",
    icon: <UserCog className="h-5 w-5" />,
    description: "Requests human input",
  },
];

// ─── Custom node styles ───────────────────────────────────────────────────────

const stateStyles: Record<NodeState, string> = {
  idle: "border-border bg-card text-muted-foreground",
  running:
    "border-blue-400 bg-blue-50 text-blue-700 dark:bg-blue-950/40 dark:text-blue-300 node-running shadow-blue-200 dark:shadow-blue-900",
  complete:
    "border-green-400 bg-green-50 text-green-700 dark:bg-green-950/40 dark:text-green-300 shadow-green-100",
  error:
    "border-red-400 bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300",
};

const iconStateStyles: Record<NodeState, string> = {
  idle: "text-muted-foreground",
  running: "text-blue-500 animate-spin",
  complete: "text-green-500",
  error: "text-red-500",
};

// ─── Custom React Flow node component ────────────────────────────────────────

interface CustomNodeData {
  label: string;
  description: string;
  icon: React.ReactNode;
  nodeState: NodeState;
  [key: string]: unknown;
}

function AgentFlowNode({ data }: { data: CustomNodeData }) {
  const { label, description, icon, nodeState } = data;

  return (
    <div
      className={cn(
        "rounded-lg border-2 px-3 py-2.5 min-w-[130px] text-center shadow-sm transition-all duration-300 select-none",
        stateStyles[nodeState]
      )}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!bg-border !w-2 !h-2"
      />

      <div
        className={cn(
          "flex justify-center mb-1.5",
          nodeState === "running" ? iconStateStyles.running : iconStateStyles[nodeState]
        )}
      >
        {icon}
      </div>

      <p className="text-xs font-semibold leading-tight">{label}</p>
      <p className="text-[10px] opacity-70 mt-0.5 leading-tight">{description}</p>

      {/* Status dot */}
      <div className="mt-1.5 flex justify-center">
        <span
          className={cn(
            "h-1.5 w-1.5 rounded-full",
            nodeState === "idle" && "bg-gray-300",
            nodeState === "running" && "bg-blue-500 animate-pulse",
            nodeState === "complete" && "bg-green-500",
            nodeState === "error" && "bg-red-500"
          )}
        />
      </div>

      <Handle
        type="source"
        position={Position.Right}
        className="!bg-border !w-2 !h-2"
      />
    </div>
  );
}

const nodeTypes: NodeTypes = {
  agentNode: AgentFlowNode,
};

// ─── AgentGraph component ─────────────────────────────────────────────────────

interface AgentGraphProps {
  nodeStates: Record<AgentNodeName, NodeState>;
}

export default function AgentGraph({ nodeStates }: AgentGraphProps) {
  const SPACING_X = 180;
  const NODE_Y = 60;

  const nodes: Node[] = useMemo(
    () =>
      NODE_CONFIGS.map((cfg, idx) => ({
        id: cfg.id,
        type: "agentNode",
        position: { x: idx * SPACING_X, y: NODE_Y },
        data: {
          label: cfg.label,
          description: cfg.description,
          icon: cfg.icon,
          nodeState: nodeStates[cfg.id] ?? "idle",
        },
        draggable: false,
        selectable: false,
      })),
    [nodeStates]
  );

  const edges: Edge[] = useMemo(
    () =>
      NODE_CONFIGS.slice(0, -1).map((cfg, idx) => ({
        id: `e-${cfg.id}-${NODE_CONFIGS[idx + 1].id}`,
        source: cfg.id,
        target: NODE_CONFIGS[idx + 1].id,
        type: "smoothstep",
        animated: nodeStates[cfg.id] === "running",
        style: {
          stroke:
            nodeStates[cfg.id] === "running"
              ? "#3b82f6"
              : nodeStates[cfg.id] === "complete"
              ? "#22c55e"
              : nodeStates[cfg.id] === "error"
              ? "#ef4444"
              : "hsl(var(--border))",
          strokeWidth: 2,
        },
      })),
    [nodeStates]
  );

  const onInit = useCallback((instance: { fitView: () => void }) => {
    instance.fitView();
  }, []);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      onInit={onInit}
      fitView
      fitViewOptions={{ padding: 0.3 }}
      proOptions={{ hideAttribution: true }}
      nodesDraggable={false}
      nodesConnectable={false}
      elementsSelectable={false}
      zoomOnScroll={false}
      panOnScroll={false}
      panOnDrag={false}
    >
      <Background
        variant={BackgroundVariant.Dots}
        gap={20}
        size={1}
        color="hsl(var(--border))"
      />
      <Controls showInteractive={false} />
    </ReactFlow>
  );
}
