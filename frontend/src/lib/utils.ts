import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export function formatNumber(n: number): string {
  return new Intl.NumberFormat().format(n);
}

export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const m = Math.floor(seconds / 60);
  const s = Math.round(seconds % 60);
  return `${m}m ${s}s`;
}

export const AGENT_COLORS: Record<string, string> = {
  researcher: "bg-blue-100 text-blue-800",
  coder: "bg-green-100 text-green-800",
  analyst: "bg-purple-100 text-purple-800",
  designer: "bg-pink-100 text-pink-800",
  writer: "bg-yellow-100 text-yellow-800",
  tester: "bg-orange-100 text-orange-800",
  integrator: "bg-teal-100 text-teal-800",
};

export const AGENT_ICONS: Record<string, string> = {
  researcher: "🔍",
  coder: "💻",
  analyst: "📊",
  designer: "🎨",
  writer: "✍️",
  tester: "🧪",
  integrator: "🔗",
};
