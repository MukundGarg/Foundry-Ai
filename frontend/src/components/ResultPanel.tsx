"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { WorkflowResult } from "@/types/workflow";
import { formatNumber, formatDuration } from "@/lib/utils";
import TaskCard from "@/components/TaskCard";
import WorkflowGraph from "@/components/WorkflowGraph";
import Badge from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";

interface ResultPanelProps {
  result: WorkflowResult;
}

export default function ResultPanel({ result }: ResultPanelProps) {
  const { project, tasks, final_result, stats } = result;

  return (
    <div className="w-full max-w-5xl mx-auto space-y-6">
      {/* Project header */}
      <Card>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-white">{project.title}</h2>
            <p className="text-gray-400 text-sm mt-1">{project.goal}</p>
          </div>
          <div className="flex flex-col items-end gap-2 shrink-0">
            <Badge>{project.domain}</Badge>
            <Badge
              variant={
                project.complexity === "high"
                  ? "error"
                  : project.complexity === "medium"
                  ? "warning"
                  : "success"
              }
            >
              {project.complexity} complexity
            </Badge>
          </div>
        </div>

        {project.key_features.length > 0 && (
          <div className="mt-4">
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">
              Key Features
            </p>
            <div className="flex flex-wrap gap-2">
              {project.key_features.map((f) => (
                <span
                  key={f}
                  className="text-xs bg-gray-800 text-gray-300 border border-gray-700 rounded-full px-3 py-1"
                >
                  {f}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Stats bar */}
        <div className="mt-4 pt-4 border-t border-gray-800 flex flex-wrap gap-4 text-xs text-gray-500">
          <span>
            ⏱ {formatDuration(stats.duration_seconds)}
          </span>
          <span>
            ✅ {stats.tasks_completed}/{tasks.length} tasks
          </span>
          {stats.tasks_failed > 0 && (
            <span className="text-red-400">❌ {stats.tasks_failed} failed</span>
          )}
          <span>
            🔤 {formatNumber(stats.total_input_tokens + stats.total_output_tokens)} tokens
          </span>
          <span>🤖 {stats.provider_used}</span>
        </div>
      </Card>

      {/* Workflow graph */}
      <div>
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
          Workflow Graph
        </h3>
        <WorkflowGraph tasks={tasks} />
      </div>

      {/* Task breakdown */}
      <div>
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
          Task Breakdown
        </h3>
        <div className="space-y-3">
          {tasks.map((task, i) => (
            <TaskCard key={task.id} task={task} index={i} />
          ))}
        </div>
      </div>

      {/* Final result */}
      <div>
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
          Final Result
        </h3>
        <Card className="prose prose-invert max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {final_result}
          </ReactMarkdown>
        </Card>
      </div>
    </div>
  );
}
