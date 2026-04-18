"use client";

import { useState } from "react";
import { WorkflowTask } from "@/types/workflow";
import { AGENT_COLORS, AGENT_ICONS } from "@/lib/utils";
import Badge from "@/components/ui/Badge";

interface TaskCardProps {
  task: WorkflowTask;
  index: number;
}

export default function TaskCard({ task, index }: TaskCardProps) {
  const [expanded, setExpanded] = useState(false);
  const icon = AGENT_ICONS[task.agent_type] || "🤖";
  const colorClass = AGENT_COLORS[task.agent_type] || "bg-gray-100 text-gray-800";

  return (
    <div
      className={`bg-gray-900 border rounded-xl overflow-hidden transition-all ${
        task.success ? "border-gray-800" : "border-red-900"
      }`}
    >
      <button
        className="w-full text-left p-4 flex items-start gap-3 hover:bg-gray-800/50 transition-colors"
        onClick={() => setExpanded((v) => !v)}
        aria-expanded={expanded}
      >
        <span className="text-xl mt-0.5" aria-hidden="true">
          {icon}
        </span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs text-gray-500 font-mono">
              #{index + 1}
            </span>
            <span className="font-medium text-gray-100 text-sm">
              {task.title}
            </span>
            <span
              className={`text-xs px-2 py-0.5 rounded-full font-medium ${colorClass}`}
            >
              {task.agent_type}
            </span>
            <Badge variant={task.success ? "success" : "error"}>
              {task.success ? "✓ Done" : "✗ Failed"}
            </Badge>
          </div>
          <div className="flex items-center gap-3 mt-1.5 text-xs text-gray-500">
            <span>{task.model}</span>
            <span>·</span>
            <span>{task.input_tokens + task.output_tokens} tokens</span>
            {task.dependencies.length > 0 && (
              <>
                <span>·</span>
                <span>depends on {task.dependencies.join(", ")}</span>
              </>
            )}
          </div>
        </div>
        <span className="text-gray-600 text-sm mt-0.5">
          {expanded ? "▲" : "▼"}
        </span>
      </button>

      {expanded && (
        <div className="px-4 pb-4 border-t border-gray-800">
          {task.error ? (
            <div className="mt-3 p-3 bg-red-950 border border-red-900 rounded-lg text-sm text-red-300">
              <strong>Error:</strong> {task.error}
            </div>
          ) : (
            <div className="mt-3">
              <p className="text-xs text-gray-500 mb-2 font-medium uppercase tracking-wide">
                Output
              </p>
              <pre className="text-xs text-gray-300 bg-gray-950 border border-gray-800 rounded-lg p-3 overflow-auto max-h-64 whitespace-pre-wrap font-mono leading-relaxed">
                {task.output}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
