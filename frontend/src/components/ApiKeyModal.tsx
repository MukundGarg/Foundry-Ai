"use client";

import { useState } from "react";
import { setApiKeys } from "@/lib/api";
import { getSessionId } from "@/lib/session";
import { ApiKeys } from "@/types/workflow";
import Button from "@/components/ui/Button";

interface ApiKeyModalProps {
  onClose: () => void;
  onSaved: (providers: string[]) => void;
}

const PROVIDERS = [
  {
    id: "openai_api_key" as keyof ApiKeys,
    label: "OpenAI",
    placeholder: "sk-...",
    hint: "GPT-4o, GPT-4 Turbo",
  },
  {
    id: "anthropic_api_key" as keyof ApiKeys,
    label: "Anthropic",
    placeholder: "sk-ant-...",
    hint: "Claude 3.5 Sonnet",
  },
  {
    id: "google_api_key" as keyof ApiKeys,
    label: "Google Gemini",
    placeholder: "AIza...",
    hint: "Gemini 1.5 Pro",
  },
  {
    id: "groq_api_key" as keyof ApiKeys,
    label: "Groq",
    placeholder: "gsk_...",
    hint: "Llama 3 70B (fast)",
  },
];

export default function ApiKeyModal({ onClose, onSaved }: ApiKeyModalProps) {
  const [keys, setKeys] = useState<ApiKeys>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSave = async () => {
    const hasKey = Object.values(keys).some((v) => v && v.trim());
    if (!hasKey) {
      setError("Please enter at least one API key.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const sessionId = getSessionId();
      const result = await setApiKeys(sessionId, keys);
      onSaved(result.providers_configured);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to save keys");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 w-full max-w-md mx-4 shadow-2xl">
        <div className="flex items-center justify-between mb-5">
          <h2 id="modal-title" className="text-lg font-semibold text-white">
            Configure API Keys
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        <p className="text-sm text-gray-400 mb-5">
          Keys are stored in memory only — never saved to disk or sent to third
          parties. Enter at least one key to continue.
        </p>

        <div className="space-y-4">
          {PROVIDERS.map((provider) => (
            <div key={provider.id}>
              <label
                htmlFor={provider.id}
                className="block text-sm font-medium text-gray-300 mb-1"
              >
                {provider.label}
                <span className="ml-2 text-xs text-gray-500 font-normal">
                  {provider.hint}
                </span>
              </label>
              <input
                id={provider.id}
                type="password"
                placeholder={provider.placeholder}
                value={keys[provider.id] || ""}
                onChange={(e) =>
                  setKeys((prev) => ({ ...prev, [provider.id]: e.target.value }))
                }
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                autoComplete="off"
              />
            </div>
          ))}
        </div>

        {error && (
          <p className="mt-3 text-sm text-red-400" role="alert">
            {error}
          </p>
        )}

        <div className="flex gap-3 mt-6">
          <Button variant="secondary" onClick={onClose} className="flex-1">
            Cancel
          </Button>
          <Button onClick={handleSave} loading={loading} className="flex-1">
            Save Keys
          </Button>
        </div>
      </div>
    </div>
  );
}
