import { cn } from "@/lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  className?: string;
  variant?: "default" | "success" | "error" | "warning";
}

export default function Badge({
  children,
  className,
  variant = "default",
}: BadgeProps) {
  const variants = {
    default: "bg-gray-800 text-gray-300 border border-gray-700",
    success: "bg-green-900/40 text-green-400 border border-green-800",
    error: "bg-red-900/40 text-red-400 border border-red-800",
    warning: "bg-yellow-900/40 text-yellow-400 border border-yellow-800",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium",
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
