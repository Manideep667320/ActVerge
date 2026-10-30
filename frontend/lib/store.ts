import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type {
  Task,
  Verdict,
  NodeState,
  AgentNodeName,
  ActionTrace,
  Evidence,
} from "./types";

interface ActVergeStore {
  tasks: Task[];
  tasksFetched: boolean;
  activeTaskId: string | null;
  activeTask: Task | null;
  activeVerdict: Verdict | null;
  activeTraces: ActionTrace[];
  activeEvidence: Evidence[];
  activeRawState: Record<string, unknown> | null;
  nodeStates: Record<AgentNodeName, NodeState>;
  sseConnected: boolean;
  sseError: string | null;

  setTasks: (tasks: Task[]) => void;
  addTask: (task: Task) => void;
  updateTask: (id: string, patch: Partial<Task>) => void;
  setActiveTask: (task: Task | null) => void;
  clearActiveTask: () => void;
  setVerdict: (verdict: Verdict) => void;
  addTrace: (trace: ActionTrace) => void;
  clearTraces: () => void;
  addEvidence: (evidence: Evidence) => void;
  clearEvidence: () => void;
  setRawState: (state: Record<string, unknown>) => void;
  updateNodeState: (node: AgentNodeName, state: NodeState) => void;
  resetNodeStates: () => void;
  setSseConnected: (connected: boolean) => void;
  setSseError: (error: string | null) => void;
}

const DEFAULT_NODE_STATES: Record<AgentNodeName, NodeState> = {
  task_interpreter: "idle",
  executor: "idle",
  state_observer: "idle",
  evidence_collector: "idle",
  outcome_verifier: "idle",
  recovery_agent: "idle",
  human_escalation: "idle",
};

export const useActVergeStore = create<ActVergeStore>()(
  devtools(
    (set) => ({
      tasks: [],
      tasksFetched: false,
      activeTaskId: null,
      activeTask: null,
      activeVerdict: null,
      activeTraces: [],
      activeEvidence: [],
      activeRawState: null,
      nodeStates: { ...DEFAULT_NODE_STATES },
      sseConnected: false,
      sseError: null,

      setTasks: (tasks) =>
        set({ tasks, tasksFetched: true }, false, "setTasks"),

      addTask: (task) =>
        set((state) => ({ tasks: [task, ...state.tasks] }), false, "addTask"),

      updateTask: (id, patch) =>
        set(
          (state) => ({
            tasks: state.tasks.map((t) =>
              t.id === id ? { ...t, ...patch } : t
            ),
            activeTask:
              state.activeTask?.id === id
                ? { ...state.activeTask, ...patch }
                : state.activeTask,
          }),
          false,
          "updateTask"
        ),

      setActiveTask: (task) =>
        set(
          { activeTask: task, activeTaskId: task?.id ?? null },
          false,
          "setActiveTask"
        ),

      clearActiveTask: () =>
        set(
          {
            activeTask: null,
            activeTaskId: null,
            activeVerdict: null,
            activeTraces: [],
            activeEvidence: [],
            activeRawState: null,
            nodeStates: { ...DEFAULT_NODE_STATES },
            sseConnected: false,
            sseError: null,
          },
          false,
          "clearActiveTask"
        ),

      setVerdict: (verdict) =>
        set({ activeVerdict: verdict }, false, "setVerdict"),

      addTrace: (trace) =>
        set(
          (state) => ({ activeTraces: [...state.activeTraces, trace] }),
          false,
          "addTrace"
        ),

      clearTraces: () => set({ activeTraces: [] }, false, "clearTraces"),

      addEvidence: (evidence) =>
        set(
          (state) => ({ activeEvidence: [...state.activeEvidence, evidence] }),
          false,
          "addEvidence"
        ),

      clearEvidence: () =>
        set({ activeEvidence: [] }, false, "clearEvidence"),

      setRawState: (rawState) =>
        set({ activeRawState: rawState }, false, "setRawState"),

      updateNodeState: (node, state) =>
        set(
          (prev) => ({ nodeStates: { ...prev.nodeStates, [node]: state } }),
          false,
          "updateNodeState"
        ),

      resetNodeStates: () =>
        set(
          { nodeStates: { ...DEFAULT_NODE_STATES } },
          false,
          "resetNodeStates"
        ),

      setSseConnected: (connected) =>
        set({ sseConnected: connected }, false, "setSseConnected"),

      setSseError: (error) =>
        set({ sseError: error }, false, "setSseError"),
    }),
    { name: "actverge-store" }
  )
);
