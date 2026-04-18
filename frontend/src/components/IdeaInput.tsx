"use client";

import { useState } from "react";
import Button from "@/components/ui/Button";
import { Provider } from "@/types/workflow";

interface IdeaInputProps {
  onRun: (idea: string, provider?: Provider) => void;
  onPlan: (idea: string, provider?: Provider) => void;
  loading: boolean;
  hasKeys: boolean;
  onConfigureKeys: () => void;
}

const EXAMPLE_IDEAS = [
  "Build a stock market AI analyst that tracks trends and generates reports",
  "Create an AI-powered resume screener for HR teams",
  "Design a personal finance tracker with spending insights",
  "Build a competitive intelligence tool that monitors competitor websites",
  "Create an AI tutor for learning Python programming",
];

const PROVIDERS: { value: Provider; label: string }[] = [
  { value: "openai", label: "OpenAI" },
  { value: "anthropic", label: "Anthropic" },
  { value: "google", label: "Google Gemini" },
  { value: "groq", label: "Groq (Fast)" },
];

export default function IdeaInput({
  onRun,
  onPlan,
  loading,
  hasKeys,
  onConfigureKeys,
}: IdeaInputProps) {
  const [idea, setIdea] = useState("");
  const [provider, setProvider] = useState<Provider | "">("");

  const handleRun = () => {
    if (!idea.trim()) return;
    onRun(idea.trim(), provider || undefined);
  };

  const handlePlan = () => {
    if (!idea.trim()) return;
    onPlan(idea.trim(), provider || undefined);
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl">
        <label
          htmlFor="idea-input"
          className="block text-sm font-medium text-gray-400 mb-2"
        >
          Describe your project idea
        </label>
        <textarea
          id="idea-input"
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          placeholder="e.g. Build a stock market AI analyst that tracks trends and generates daily reports..."
          rows={4}
          className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-gray-100 placeholder-gray-600 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition-all"
          disabled={loading}
        />

        {/* Example ideas */}
        <div className="mt-3 flex flex-wrap gap-2">
          {EXAMPLE_IDEAS.slice(0, 3).map((ex) => (
            <button
              key={ex}
              onClick={() => setIdea(ex)}
              className="text-xs text-gray-500 hover:text-brand-400 bg-gray-800 hover:bg-gray-750 border border-gray-700 rounded-full px-3 py-1 transition-colors truncate max-w-[200px]"
              title={ex}
              disabled={loading}
            >
              {ex.slice(0, 40)}…
            </button>
          ))}
        </div>

        <div className="flex items-center gap-3 mt-4">
          {/* Provider selector */}
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value as Provider | "")}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:ring-2 focus:ring-brand-500"
            disabled={loading}
            aria-label="Select AI provider"
          >
            <option value="">Auto-select provider</option>
            {PROVIDERS.map((p) => (
              <option key={p.value} value={p.value}>
                {p.label}
              </option>
            ))}
          </select>

          <div className="flex-1" />

          {!hasKeys && (
            <Button variant="secondary" size="sm" onClick={onConfigureKeys}>
              🔑 Add API Keys
            </Button>
          )}

          <Button
            variant="secondary"
            size="md"
            onClick={handlePlan}
            disabled={!idea.trim() || loading || !hasKeys}
          >
            Preview Plan
          </Button>

          <Button
            variant="primary"
            size="md"
            onClick={handleRun}
            loading={loading}
            disabled={!idea.trim() || !hasKeys}
          >
            {loading ? "Running…" : "Run Workflow ▶"}
          </Button>
        </div>

        {!hasKeys && (
          <p className="mt-3 text-xs text-yellow-500">
            ⚠ Configure at least one API key to run workflows.
          </p>
        )}
      </div>
    </div>
  );
}
