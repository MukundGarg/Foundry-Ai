export type Provider = "openai" | "anthropic" | "google" | "groq";

export interface ApiKeys {
  openai_api_key?: string;
  anthropic_api_key?: string;
  google_api_key?: string;
  groq_api_key?: string;
}

export interface ProjectInfo {
  title: string;
  domain: string;
  goal: string;
  key_features: string[];
  complexity: "low" | "medium" | "high";
  suggested_stack: string[];
}

export type TaskType =
  | "research"
  | "coding"
  | "analysis"
  | "design"
  | "writing"
  | "testing"
  | "integration";

export type AgentType =
  | "researcher"
  | "coder"
  | "analyst"
  | "designer"
  | "writer"
  | "tester"
  | "integrator";

export interface WorkflowTask {
  id: string;
  title: string;
  type: TaskType;
  agent_type: AgentType;
  dependencies: string[];
  parallel_safe: boolean;
  success: boolean;
  output: string;
  output_preview: string;
  provider: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  error?: string;
}

export interface WorkflowStats {
  total_input_tokens: number;
  total_output_tokens: number;
  provider_used: string;
  duration_seconds: number;
  tasks_completed: number;
  tasks_failed: number;
}

export interface WorkflowResult {
  idea: string;
  project: ProjectInfo;
  tasks: WorkflowTask[];
  final_result: string;
  stats: WorkflowStats;
  success: boolean;
}

export interface WorkflowPlan {
  idea: string;
  project: ProjectInfo;
  tasks: Omit<WorkflowTask, "success" | "output" | "output_preview" | "provider" | "model" | "input_tokens" | "output_tokens">[];
  provider: string;
}

export type WorkflowStatus = "idle" | "planning" | "executing" | "done" | "error";
