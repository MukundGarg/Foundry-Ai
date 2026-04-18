"use client";

import { WorkflowPlan } from "@/types/workflow";
import { AGENT_COLORS, AGENT_ICONS } from "@/lib/utils";
import WorkflowGraph from "@/components/WorkflowGraph";
import { Card } from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";

interface PlanPreviewProps {
  plan: WorkflowPlan;
  onRun: () => void;
  loading: boolean;
}

export default function PlanPreview({ plan, onRun, loading }: PlanPreviewProps) {
  return (
    <div className="w-full max-w-5xl mx-auto space-y-6">
      <Card>
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-xl font-bold text-white">{plan.project.title}</h2>
            <p className="text-gray-400 text-sm mt-1">{plan.project.goal}</p>
          </div>
          <Badge>{plan.provider}</Badge>
        </div>
        <p className="text-xs text-gray-500 mt-3">
          {plan.tasks.length} tasks planned · Review the workflow below, then run it.
        </p>
      </Card>

      <div>
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
          Workflow Graph
        </h3>
        <WorkflowGraph tasks={plan.tasks as any} />
      </div>

      <div>
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
          Planned Tasks
        </h3>
        <div className="space-y-2">
          {plan.tasks.map((task, i) => {
            const icon = AGENT_ICONS[task.agent_type] || "🤖";
            const colorClass = AGENT_COLORS[task.agent_type] || "";
            return (
              <div
                key={task.id}
                className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex items-start gap-3"
              >
                <span className="text-xl mt-0.5">{icon}</span>
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs text-gray-500 font-mono">#{i + 1}</span>
                    <span className="font-medium text-gray-100 text-sm">{task.title}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${colorClass}`}>
                      {task.agent_type}
                    </span>
                    {task.parallel_safe && (
                      <Badge>⚡ parallel</Badge>
                    )}
                  </div>
                  <p className="text-xs text-gray-400 mt-1">{(task as any).description}</p>
                  {task.dependencies.length > 0 && (
                    <p className="text-xs text-gray-600 mt-1">
                      Depends on: {task.dependencies.join(", ")}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="flex justify-end">
        <Button size="lg" onClick={onRun} loading={loading}>
          Execute This Workflow ▶
        </Button>
      </div>
    </div>
  );
}
