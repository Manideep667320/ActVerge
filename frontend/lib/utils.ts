import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { formatDistanceToNow, format } from "date-fns";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatSafeDistance(timestamp?: string | null): string {
  if (!timestamp) return "just now";
  try {
    const d = new Date(timestamp);
    if (isNaN(d.getTime())) return "just now";
    return formatDistanceToNow(d, { addSuffix: true });
  } catch {
    return "just now";
  }
}

export function formatSafeDate(timestamp?: string | null, pattern = "MMM d, HH:mm"): string {
  if (!timestamp) return "—";
  try {
    const d = new Date(timestamp);
    if (isNaN(d.getTime())) return "—";
    return format(d, pattern);
  } catch {
    return "—";
  }
}

