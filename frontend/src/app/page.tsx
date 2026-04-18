"use client";

import { useState, useEffect } from "react";
import { runWorkflow, planWorkflow, getConfiguredProviders } from "@/lib/api";
import { getSessionId } from "@/lib/session";
import { WorkflowResult, WorkflowPlan, WorkflowStatus, Provider } from "@/types/workflow";
import IdeaInput from "@/components/IdeaInput";
import ApiKeyModal from "@/components/ApiKeyModal";
import ResultPanel from "@/components/ResultPanel";
import PlanPreview from "@/components/PlanPreview";

export default function HomePage() {
  const [status, setStatus] = useState<WorkflowStatus>("idle");
  const [result, setResult] = useState<WorkflowResult | null>(null);
  const [plan, setPlan] = useState<WorkflowPlan | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [configuredProviders, setConfiguredProviders] = useState<string[]>([]);
  const [pendingIdea, setPendingIdea] = useState<string>("");
  const [pendingProvider, setPendingProvider] = useState<Provider | undefined>();

  // Check if keys are already configured for this session
  useEffect(() => {
    const sessionId = getSessionId();
    getConfiguredProviders(sessionId)
      .then((r) => setConfiguredProviders(r.providers_configured))
      .catch(() => {});
  }, []);

  const hasKeys = configuredProviders.length > 0;

  const handleRun = async (idea: string, provider?: Provider) => {
    setError(null);
    setPlan(null);
    setResult(null);
    setStatus("executing");
    try {
      const sessionId = getSessionId();
      const res = await runWorkflow(sessionId, idea, provider);
      setResult(res);
      setStatus("done");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Workflow failed");
      setStatus("error");
    }
  };

  const handlePlan = async (idea: string, provider?: Provider) => {
    setError(null);
    setPlan(null);
    setResult(null);
    setStatus("planning");
    setPendingIdea(idea);
    setPendingProvider(provider);
    try {
      const sessionId = getSessionId();
      const res = await planWorkflow(sessionId, idea, provider);
      setPlan(res);
      setStatus("idle");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Planning failed");
      setStatus("error");
    }
  };

  const handleRunFromPlan = () => {
    if (pendingIdea) {
      handleRun(pendingIdea, pendingProvider);
    }
  };

  const handleKeysSaved = (providers: string[]) => {
    setConfiguredProviders(providers);
    setShowKeyModal(false);
  };

  const isLoading = status === "planning" || status === "executing";

  return (
    <main className="min-h-screen bg-[#0a0a0f]">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-950/80 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl" aria-hidden="true">⚡</span>
            <div>
              <h1 className="text-base font-bold text-white leading-none">
                Foundry AI
              </h1>
              <p className="text-xs text-gray-500">Workflow Builder</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {hasKeys && (
              <div className="flex items-center gap-1.5">
                {configuredProviders.map((p) => (
                  <span
                    key={p}
                    className="text-xs bg-green-900/40 text-green-400 border border-green-800 rounded-full px-2 py-0.5"
                  >
                    {p}
                  </span>
                ))}
              </div>
            )}
            <button
              onClick={() => setShowKeyModal(true)}
              className="text-xs text-gray-400 hover:text-white bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg px-3 py-1.5 transition-colors"
            >
              🔑 {hasKeys ? "Edit Keys" : "Add Keys"}
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-10 space-y-10">
        {/* Hero */}
        {status === "idle" && !result && !plan && (
          <div className="text-center mb-8">
            <h2 className="text-4xl font-bold text-white mb-3">
              Turn any idea into a{" "}
              <span className="text-brand-400">working result</span>
            </h2>
            <p className="text-gray-400 text-lg max-w-xl mx-auto">
              Describe your project. Foundry AI plans the tasks, assigns the
              right agents, and executes the full workflow automatically.
            </p>
          </div>
        )}

        {/* Input */}
        <IdeaInput
          onRun={handleRun}
          onPlan={handlePlan}
          loading={isLoading}
          hasKeys={hasKeys}
          onConfigureKeys={() => setShowKeyModal(true)}
        />

        {/* Status indicator */}
        {isLoading && (
          <div className="flex flex-col items-center gap-3 py-12">
            <div className="flex gap-2">
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className="w-2.5 h-2.5 bg-brand-500 rounded-full animate-bounce"
                  style={{ animationDelay: `${i * 0.15}s` }}
                />
              ))}
            </div>
            <p className="text-gray-400 text-sm">
              {status === "planning"
                ? "Analyzing your idea and building the workflow plan…"
                : "Executing workflow — agents are working in parallel…"}
            </p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div
            className="max-w-3xl mx-auto bg-red-950 border border-red-900 rounded-xl p-4 text-red-300 text-sm"
            role="alert"
          >
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Plan preview */}
        {plan && !result && (
          <PlanPreview
            plan={plan}
            onRun={handleRunFromPlan}
            loading={isLoading}
          />
        )}

        {/* Full result */}
        {result && <ResultPanel result={result} />}
      </div>

      {/* API Key Modal */}
      {showKeyModal && (
        <ApiKeyModal
          onClose={() => setShowKeyModal(false)}
          onSaved={handleKeysSaved}
        />
      )}
    </main>
  );
}
