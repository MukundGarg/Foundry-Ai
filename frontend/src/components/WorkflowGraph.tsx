"use client";

import { useMemo } from "react";
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  MarkerType,
  BackgroundVariant,
} from "reactflow";
import "reactflow/dist/style.css";
import { WorkflowTask } from "@/types/workflow";
import { AGENT_COLORS, AGENT_ICONS } from "@/lib/utils";

interface WorkflowGraphProps {
  tasks: WorkflowTask[] | Omit<WorkflowTask, "success" | "output" | "output_preview" | "provider" | "model" | "input_tokens" | "output_tokens">[];
}

const NODE_WIDTH = 180;
const NODE_HEIGHT = 80;
const H_GAP = 60;
const V_GAP = 40;

function layoutNodes(tasks: WorkflowGraphProps["tasks"]): Node[] {
  // Topological sort to assign levels
  const levels: Record<string, number> = {};
  const taskMap = new Map(tasks.map((t) => [t.id, t]));

  function getLevel(id: string): number {
    if (id in levels) return levels[id];
    const task = taskMap.get(id);
    if (!task || task.dependencies.length === 0) {
      levels[id] = 0;
      return 0;
    }
    const maxDepLevel = Math.max(...task.dependencies.map(getLevel));
    levels[id] = maxDepLevel + 1;
    return levels[id];
  }

  tasks.forEach((t) => getLevel(t.id));

  // Group by level
  const byLevel: Record<number, typeof tasks> = {};
  tasks.forEach((t) => {
    const lvl = levels[t.id] ?? 0;
    if (!byLevel[lvl]) byLevel[lvl] = [];
    byLevel[lvl].push(t);
  });

  const nodes: Node[] = [];
  Object.entries(byLevel).forEach(([lvlStr, levelTasks]) => {
    const lvl = parseInt(lvlStr);
    levelTasks.forEach((task, idx) => {
      const colorClass = AGENT_COLORS[task.agent_type] || "bg-gray-100 text-gray-800";
      const icon = AGENT_ICONS[task.agent_type] || "🤖";
      const isSuccess = "success" in task ? task.success : undefined;

      nodes.push({
        id: task.id,
        position: {
          x: lvl * (NODE_WIDTH + H_GAP),
          y: idx * (NODE_HEIGHT + V_GAP),
        },
        data: {
          label: (
            <div className="text-left p-1">
              <div className="flex items-center gap-1 mb-1">
                <span>{icon}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${colorClass}`}>
                  {task.agent_type}
                </span>
                {isSuccess !== undefined && (
                  <span className="ml-auto text-xs">
                    {isSuccess ? "✅" : "❌"}
                  </span>
                )}
              </div>
              <div className="text-xs font-semibold text-gray-800 leading-tight">
                {task.title}
              </div>
            </div>
          ),
        },
        style: {
          width: NODE_WIDTH,
          minHeight: NODE_HEIGHT,
          background: isSuccess === false ? "#fef2f2" : "#ffffff",
          border: `1px solid ${isSuccess === false ? "#fca5a5" : isSuccess === true ? "#86efac" : "#e5e7eb"}`,
          borderRadius: "10px",
          fontSize: "12px",
          padding: "6px",
        },
      });
    });
  });

  return nodes;
}

function buildEdges(tasks: WorkflowGraphProps["tasks"]): Edge[] {
  const edges: Edge[] = [];
  tasks.forEach((task) => {
    task.dependencies.forEach((depId) => {
      edges.push({
        id: `${depId}->${task.id}`,
        source: depId,
        target: task.id,
        markerEnd: { type: MarkerType.ArrowClosed, color: "#6366f1" },
        style: { stroke: "#6366f1", strokeWidth: 1.5 },
        animated: true,
      });
    });
  });
  return edges;
}

export default function WorkflowGraph({ tasks }: WorkflowGraphProps) {
  const nodes = useMemo(() => layoutNodes(tasks), [tasks]);
  const edges = useMemo(() => buildEdges(tasks), [tasks]);

  return (
    <div className="w-full h-[400px] rounded-xl overflow-hidden border border-gray-800 bg-gray-950">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        proOptions={{ hideAttribution: true }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={16}
          size={1}
          color="#1f2937"
        />
        <Controls showInteractive={false} />
        <MiniMap
          nodeColor={() => "#4f62fa"}
          maskColor="rgba(0,0,0,0.6)"
          style={{ background: "#111827" }}
        />
      </ReactFlow>
    </div>
  );
}
