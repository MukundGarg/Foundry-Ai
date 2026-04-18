import { ApiKeys, WorkflowResult, WorkflowPlan, Provider } from "@/types/workflow";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `Request failed: ${res.status}`);
  }

  return res.json() as Promise<T>;
}

// ── API Keys ──────────────────────────────────────────────────────────────────

export async function setApiKeys(
  sessionId: string,
  keys: ApiKeys
): Promise<{ providers_configured: string[] }> {
  return request("/api/keys/set", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, ...keys }),
  });
}

export async function getConfiguredProviders(
  sessionId: string
): Promise<{ providers_configured: string[] }> {
  return request(`/api/keys/providers/${sessionId}`);
}

export async function clearApiKeys(sessionId: string): Promise<void> {
  await request(`/api/keys/clear/${sessionId}`, { method: "DELETE" });
}

// ── Workflow ──────────────────────────────────────────────────────────────────

export async function runWorkflow(
  sessionId: string,
  idea: string,
  preferredProvider?: Provider
): Promise<WorkflowResult> {
  return request("/api/workflow/run", {
    method: "POST",
    body: JSON.stringify({
      session_id: sessionId,
      idea,
      preferred_provider: preferredProvider,
    }),
  });
}

export async function planWorkflow(
  sessionId: string,
  idea: string,
  preferredProvider?: Provider
): Promise<WorkflowPlan> {
  return request("/api/workflow/plan", {
    method: "POST",
    body: JSON.stringify({
      session_id: sessionId,
      idea,
      preferred_provider: preferredProvider,
    }),
  });
}

// ── Health ────────────────────────────────────────────────────────────────────

export async function checkHealth(): Promise<{ status: string }> {
  return request("/api/health");
}
