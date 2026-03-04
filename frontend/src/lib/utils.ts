/* ============================================
 * STTS Utility Functions
 * ============================================ */

import type { TicketPriority, TicketCategory, TicketStatus } from "@/types";

/** Format a UTC datetime string as relative time (e.g. "2h ago") */
export function timeAgo(dateStr: string): string {
    const now = new Date();
    // Backend sends UTC timestamps — ensure JS parses them as UTC, not local time
    const utcStr = dateStr.endsWith("Z") || dateStr.includes("+") ? dateStr : dateStr + "Z";
    const date = new Date(utcStr);
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (seconds < 60) return "just now";
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days < 30) return `${days}d ago`;
    return date.toLocaleDateString();
}

/** Priority color classes */
export function priorityColor(p: TicketPriority | null): string {
    switch (p) {
        case "High":
            return "bg-red-500/15 text-red-400 border-red-500/30";
        case "Medium":
            return "bg-amber-500/15 text-amber-400 border-amber-500/30";
        case "Low":
            return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
        default:
            return "bg-zinc-500/15 text-zinc-400 border-zinc-500/30";
    }
}

/** Category color classes */
export function categoryColor(c: TicketCategory | null): string {
    switch (c) {
        case "Billing":
            return "bg-violet-500/15 text-violet-400 border-violet-500/30";
        case "Technical Bug":
            return "bg-rose-500/15 text-rose-400 border-rose-500/30";
        case "Feature Request":
            return "bg-sky-500/15 text-sky-400 border-sky-500/30";
        case "Account":
            return "bg-orange-500/15 text-orange-400 border-orange-500/30";
        case "General":
            return "bg-zinc-500/15 text-zinc-400 border-zinc-500/30";
        default:
            return "bg-zinc-500/15 text-zinc-400 border-zinc-500/30";
    }
}

/** Status color classes */
export function statusColor(s: TicketStatus): string {
    switch (s) {
        case "Open":
            return "bg-blue-500/15 text-blue-400 border-blue-500/30";
        case "In Progress":
            return "bg-amber-500/15 text-amber-400 border-amber-500/30";
        case "Resolved":
            return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
    }
}
