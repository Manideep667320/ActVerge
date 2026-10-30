import { cn } from "@/lib/utils";
import type { VerdictType } from "@/lib/types";
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  Clock,
} from "lucide-react";

const CONFIG: Record<
  VerdictType,
  { label: string; className: string; icon: React.ReactNode }
> = {
  SUCCESS: {
    label: "Success",
    className:
      "bg-green-100 text-green-800 border-green-300 dark:bg-green-900/30 dark:text-green-400 dark:border-green-700",
    icon: <CheckCircle2 className="h-3.5 w-3.5" />,
  },
  PARTIAL: {
    label: "Partial",
    className:
      "bg-yellow-100 text-yellow-800 border-yellow-300 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-700",
    icon: <AlertTriangle className="h-3.5 w-3.5" />,
  },
  FAILED: {
    label: "Failed",
    className:
      "bg-red-100 text-red-800 border-red-300 dark:bg-red-900/30 dark:text-red-400 dark:border-red-700",
    icon: <XCircle className="h-3.5 w-3.5" />,
  },
  UNCERTAIN: {
    label: "Uncertain",
    className:
      "bg-gray-100 text-gray-600 border-gray-300 dark:bg-gray-800/50 dark:text-gray-400 dark:border-gray-600",
    icon: <HelpCircle className="h-3.5 w-3.5" />,
  },
  PENDING: {
    label: "Pending",
    className:
      "bg-blue-100 text-blue-700 border-blue-300 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-700",
    icon: <Clock className="h-3.5 w-3.5" />,
  },
};

interface VerdictBadgeProps {
  verdict: VerdictType;
  size?: "sm" | "md" | "lg";
  showIcon?: boolean;
  className?: string;
}

export default function VerdictBadge({
  verdict,
  size = "sm",
  showIcon = true,
  className,
}: VerdictBadgeProps) {
  const config = CONFIG[verdict] ?? CONFIG.UNCERTAIN;

  const sizeClass = {
    sm: "text-xs px-2 py-0.5 gap-1",
    md: "text-sm px-2.5 py-1 gap-1.5",
    lg: "text-base px-3 py-1.5 gap-2",
  }[size];

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border font-semibold",
        sizeClass,
        config.className,
        className
      )}
    >
      {showIcon && config.icon}
      {config.label}
    </span>
  );
}
