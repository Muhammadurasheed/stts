"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { ticketsAPI } from "@/lib/api";
import { timeAgo, priorityColor, categoryColor, statusColor } from "@/lib/utils";
import type { Ticket, TicketStatus, TicketPriority, TicketCategory } from "@/types";
import {
    Plus,
    Pencil,
    Trash2,
    RefreshCw,
    LogOut,
    LayoutGrid,
    List,
    Search,
    Filter,
    MoreHorizontal,
    X,
    AlertCircle,
    CheckCircle2,
    Clock,
    Sparkles
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

type ViewMode = "kanban" | "table";

export default function DashboardPage() {
    const { agent, isLoading: authLoading, isAuthenticated, logout } = useAuth();
    const router = useRouter();
    const [tickets, setTickets] = useState<Ticket[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState("");
    const [viewMode, setViewMode] = useState<ViewMode>("kanban");
    // Filter & Search state
    const [searchQuery, setSearchQuery] = useState("");
    const [filterStatus, setFilterStatus] = useState<string>("");
    const [filterPriority, setFilterPriority] = useState<string>("");
    const [updatingId, setUpdatingId] = useState<string | null>(null);

    // Modal state
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [editingTicket, setEditingTicket] = useState<Ticket | null>(null);
    const [deletingTicket, setDeletingTicket] = useState<Ticket | null>(null);

    // ── Auth guard ─────────────────────────────
    useEffect(() => {
        // CRITICAL: Only redirect AFTER auth is fully resolved
        // Never redirect while still loading/hydrating
        if (!authLoading && !isAuthenticated) {
            router.push("/login");
        }
    }, [authLoading, isAuthenticated, router]);


    // ── Fetch tickets ──────────────────────────
    const fetchTickets = useCallback(async () => {
        setIsLoading(true);
        setError("");
        try {
            console.log("[STTS] fetchTickets: Fetching from API...");
            const data = await ticketsAPI.list({ page: 1, page_size: 200 });
            console.log("[STTS] fetchTickets: Got", data.items.length, "tickets, total:", data.total);
            setTickets(data.items);
        } catch (err: unknown) {
            console.error("[STTS] fetchTickets ERROR:", err);
            setError(err instanceof Error ? err.message : "Failed to load tickets");
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        if (isAuthenticated) fetchTickets();
    }, [isAuthenticated, fetchTickets]);

    // ── Handlers ───────────────────────────────
    const handleStatusUpdate = async (ticketId: string, newStatus: TicketStatus) => {
        setUpdatingId(ticketId);
        setTickets((prev) =>
            prev.map((t) => (t.id === ticketId ? { ...t, status: newStatus } : t))
        );

        try {
            await ticketsAPI.updateStatus(ticketId, { status: newStatus });
        } catch {
            fetchTickets();
        } finally {
            setUpdatingId(null);
        }
    };

    const handleDelete = async (ticketId: string) => {
        try {
            await ticketsAPI.delete(ticketId);
            setTickets((prev) => prev.filter((t) => t.id !== ticketId));
            setDeletingTicket(null);
        } catch (err) {
            setError("Failed to delete ticket");
        }
    };

    const handleCreateSuccess = (newTicket: Ticket) => {
        setTickets((prev) => [newTicket, ...prev]);
        setIsCreateModalOpen(false);
    };

    const handleEditSuccess = (updatedTicket: Ticket) => {
        setTickets((prev) =>
            prev.map((t) => (t.id === updatedTicket.id ? updatedTicket : t))
        );
        setEditingTicket(null);
    };

    // ── Filtered data & Stats ──────────────────
    // Stats always use the FULL fetched list for global overview
    const stats = {
        total: tickets.length,
        open: tickets.filter((t) => t.status === "Open").length,
        inProgress: tickets.filter((t) => t.status === "In Progress").length,
        resolved: tickets.filter((t) => t.status === "Resolved").length,
        highPriority: tickets.filter((t) => t.priority === "High").length,
    };

    // Derived filtered list for display
    const filteredTickets = tickets.filter((t) => {
        const matchesSearch =
            searchQuery === "" ||
            t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            t.customer_email.toLowerCase().includes(searchQuery.toLowerCase()) ||
            t.id.toLowerCase().includes(searchQuery.toLowerCase());

        const matchesStatus = filterStatus === "" || t.status === filterStatus;
        const matchesPriority = filterPriority === "" || t.priority === filterPriority;

        return matchesSearch && matchesStatus && matchesPriority;
    });

    if (authLoading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-[#050505]">
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex flex-col items-center gap-4"
                >
                    <div className="h-10 w-10 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
                    <p className="text-sm font-medium text-zinc-500 tracking-wide">Syncing STTS...</p>
                </motion.div>
            </div>
        );
    }

    if (!isAuthenticated) return null;

    return (
        <div className="min-h-screen bg-[#050505] text-white selection:bg-indigo-500/30">
            {/* ── Background Elements ──────────────── */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-500/10 blur-[120px] rounded-full" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-violet-600/10 blur-[120px] rounded-full" />
            </div>

            {/* ── Top Nav ─────────────────────────── */}
            <header className="border-b border-white/[0.05] bg-black/40 backdrop-blur-2xl sticky top-0 z-40">
                <div className="mx-auto flex h-20 items-center justify-between px-6 lg:px-10">
                    <div className="flex items-center gap-5">
                        <motion.div
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 shadow-lg shadow-indigo-500/20"
                        >
                            <Sparkles className="h-6 w-6 text-white" />
                        </motion.div>
                        <div className="hidden sm:block">
                            <h1 className="text-xl font-bold tracking-tight text-white">STTS Dashboard</h1>
                            <p className="text-xs font-medium text-zinc-500">
                                {agent?.full_name} <span className="mx-1.5 opacity-30">•</span> {agent?.role}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        {agent?.picture_url && (
                            <motion.img
                                initial={{ opacity: 0, scale: 0.8 }}
                                animate={{ opacity: 1, scale: 1 }}
                                src={agent.picture_url}
                                alt={agent.full_name}
                                className="h-10 w-10 rounded-full border-2 border-white/10 shadow-lg"
                                referrerPolicy="no-referrer"
                            />
                        )}
                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => setIsCreateModalOpen(true)}
                            className="flex items-center gap-2 rounded-xl bg-white px-5 py-2.5 text-sm font-bold text-black shadow-sm transition-all hover:bg-zinc-100"
                        >
                            <Plus className="h-4 w-4" />
                            <span>New Ticket</span>
                        </motion.button>
                        <button
                            onClick={logout}
                            className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/[0.08] bg-white/[0.03] text-zinc-400 transition-all hover:bg-white/[0.08] hover:text-white"
                            title="Sign Out"
                        >
                            <LogOut className="h-4 w-4" />
                        </button>
                    </div>
                </div>
            </header>

            <main className="mx-auto max-w-[1400px] px-6 py-10 lg:px-10">
                {/* ── Header Area ──────────────────── */}
                <div className="mb-10 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
                    <div>
                        <h2 className="text-3xl font-bold tracking-tight text-white">Tickets Overview</h2>
                        <p className="mt-1 text-zinc-500">Manage and resolve triaged support requests.</p>
                    </div>

                    <div className="flex flex-wrap items-center gap-3">
                        <div className="flex items-center rounded-xl border border-white/[0.08] bg-white/[0.02] p-1 shadow-inner">
                            {(["kanban", "table"] as ViewMode[]).map((v) => (
                                <button
                                    key={v}
                                    onClick={() => setViewMode(v)}
                                    className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-bold transition-all ${viewMode === v
                                        ? "bg-white/[0.1] text-white shadow-sm"
                                        : "text-zinc-500 hover:text-zinc-300"
                                        }`}
                                >
                                    {v === "kanban" ? <LayoutGrid className="h-3.5 w-3.5" /> : <List className="h-3.5 w-3.5" />}
                                    <span className="capitalize">{v}</span>
                                </button>
                            ))}
                        </div>
                        <button
                            onClick={fetchTickets}
                            className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/[0.08] bg-white/[0.02] text-zinc-500 transition-all hover:bg-white/[0.08] hover:text-white"
                            title="Refresh"
                        >
                            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                        </button>
                    </div>
                </div>

                {/* ── Stats Chips ─────────────────── */}
                <div className="mb-10 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
                    {[
                        { label: "Total", value: stats.total, color: "text-white", bg: "bg-white/5", icon: <Filter className="h-3 w-3" /> },
                        { label: "Open", value: stats.open, color: "text-blue-400", bg: "bg-blue-500/10", icon: <Clock className="h-3 w-3" /> },
                        { label: "In Progress", value: stats.inProgress, color: "text-amber-400", bg: "bg-amber-500/10", icon: <AlertCircle className="h-3 w-3" /> },
                        { label: "Resolved", value: stats.resolved, color: "text-emerald-400", bg: "bg-emerald-500/10", icon: <CheckCircle2 className="h-3 w-3" /> },
                        { label: "High Severity", value: stats.highPriority, color: "text-red-400", bg: "bg-red-500/10", icon: <Sparkles className="h-3 w-3" /> },
                    ].map((s) => (
                        <div
                            key={s.label}
                            className={`flex flex-col justify-between rounded-2xl p-5 border border-white/[0.05] shadow-sm transition-all hover:border-white/[0.1] hover:bg-white/[0.02] ${s.bg}`}
                        >
                            <div className="flex items-center gap-2">
                                <span className={s.color}>{s.icon}</span>
                                <p className="text-[10px] font-bold uppercase tracking-widest text-zinc-500">{s.label}</p>
                            </div>
                            <p className={`mt-4 text-3xl font-bold ${s.color}`}>{s.value}</p>
                        </div>
                    ))}
                </div>

                {/* ── Filters ──────────────────────── */}
                <div className="mb-8 flex flex-wrap items-center gap-4">
                    <div className="relative flex-1 min-w-[240px] max-w-md">
                        <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Search tickets by ID, title, or email..."
                            className="w-full rounded-xl border border-white/[0.08] bg-white/[0.02] py-2.5 pl-10 pr-4 text-sm text-zinc-300 placeholder:text-zinc-600 focus:border-indigo-500/50 focus:outline-none focus:ring-1 focus:ring-indigo-500/20"
                        />
                    </div>

                    <div className="flex items-center gap-3">
                        <select
                            value={filterStatus}
                            onChange={(e) => setFilterStatus(e.target.value)}
                            className="rounded-xl border border-white/[0.08] bg-white/[0.02] px-4 py-2.5 text-xs font-bold text-zinc-400 focus:border-indigo-500/50 focus:outline-none"
                        >
                            <option value="">All Statuses</option>
                            <option value="Open">Open</option>
                            <option value="In Progress">In Progress</option>
                            <option value="Resolved">Resolved</option>
                        </select>
                        <select
                            value={filterPriority}
                            onChange={(e) => setFilterPriority(e.target.value)}
                            className="rounded-xl border border-white/[0.08] bg-white/[0.02] px-4 py-2.5 text-xs font-bold text-zinc-400 focus:border-indigo-500/50 focus:outline-none"
                        >
                            <option value="">All Severities</option>
                            <option value="High">High Severity</option>
                            <option value="Medium">Medium Severity</option>
                            <option value="Low">Low Severity</option>
                        </select>
                    </div>
                </div>

                {/* ── Content Views ────────────────── */}
                <AnimatePresence mode="wait">
                    {isLoading ? (
                        <motion.div
                            key="loading"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="flex h-96 items-center justify-center"
                        >
                            <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
                        </motion.div>
                    ) : viewMode === "kanban" ? (
                        <KanbanView
                            tickets={filteredTickets}
                            updatingId={updatingId}
                            onUpdateStatus={handleStatusUpdate}
                            onEdit={setEditingTicket}
                            onDelete={setDeletingTicket}
                        />
                    ) : (
                        <TableView
                            tickets={filteredTickets}
                            updatingId={updatingId}
                            onUpdateStatus={handleStatusUpdate}
                            onEdit={setEditingTicket}
                            onDelete={setDeletingTicket}
                        />
                    )}
                </AnimatePresence>
            </main>

            {/* ── Modals ─────────────────────────── */}
            <AnimatePresence>
                {isCreateModalOpen && (
                    <TicketModal
                        title="Submit New Ticket"
                        onClose={() => setIsCreateModalOpen(false)}
                        onSuccess={handleCreateSuccess}
                        mode="create"
                    />
                )}
                {editingTicket && (
                    <TicketModal
                        title="Edit Ticket"
                        onClose={() => setEditingTicket(null)}
                        onSuccess={handleEditSuccess}
                        mode="edit"
                        ticket={editingTicket}
                    />
                )}
                {deletingTicket && (
                    <DeleteConfirmationModal
                        ticket={deletingTicket}
                        onClose={() => setDeletingTicket(null)}
                        onConfirm={() => handleDelete(deletingTicket.id)}
                    />
                )}
            </AnimatePresence>
        </div>
    );
}

// ── Kanban View ─────────────────────────────

function KanbanView({
    tickets,
    updatingId,
    onUpdateStatus,
    onEdit,
    onDelete
}: {
    tickets: Ticket[],
    updatingId: string | null,
    onUpdateStatus: (id: string, s: TicketStatus) => void,
    onEdit: (t: Ticket) => void,
    onDelete: (t: Ticket) => void
}) {
    const columns: { status: TicketStatus; label: string; color: string }[] = [
        { status: "Open", label: "Open", color: "bg-blue-500" },
        { status: "In Progress", label: "In Progress", color: "bg-amber-500" },
        { status: "Resolved", label: "Resolved", color: "bg-emerald-500" },
    ];

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="grid grid-cols-1 gap-6 lg:grid-cols-3"
        >
            {columns.map((col) => {
                const colTickets = tickets.filter((t) => t.status === col.status);
                return (
                    <div key={col.status} className="flex flex-col gap-5">
                        <div className="flex items-center justify-between pb-1">
                            <div className="flex items-center gap-3">
                                <div className={`h-2 w-2 rounded-full ${col.color} shadow-[0_0_8px_rgba(59,130,246,0.5)]`} />
                                <h3 className="text-sm font-bold tracking-tight text-white/90">{col.label}</h3>
                                <div className="rounded-md bg-white/[0.05] px-2 py-0.5 text-[10px] font-bold text-zinc-500">
                                    {colTickets.length}
                                </div>
                            </div>
                        </div>

                        <div className="flex flex-col gap-4 min-h-[500px]">
                            {colTickets.length === 0 && (
                                <div className="rounded-2xl border border-dashed border-white/[0.05] bg-white/[0.01] py-20 text-center">
                                    <p className="text-xs font-medium text-zinc-600">No tickets in this state</p>
                                </div>
                            )}
                            <AnimatePresence>
                                {colTickets.map((ticket) => (
                                    <TicketCard
                                        key={ticket.id}
                                        ticket={ticket}
                                        isUpdating={updatingId === ticket.id}
                                        onUpdateStatus={onUpdateStatus}
                                        onEdit={() => onEdit(ticket)}
                                        onDelete={() => onDelete(ticket)}
                                    />
                                ))}
                            </AnimatePresence>
                        </div>
                    </div>
                );
            })}
        </motion.div>
    );
}

// ── Ticket Card ─────────────────────────────

function TicketCard({
    ticket,
    isUpdating,
    onUpdateStatus,
    onEdit,
    onDelete
}: {
    ticket: Ticket,
    isUpdating: boolean,
    onUpdateStatus: (id: string, s: TicketStatus) => void,
    onEdit: () => void,
    onDelete: () => void
}) {
    return (
        <motion.div
            layout
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            whileHover={{ y: -4, backgroundColor: "rgba(255, 255, 255, 0.04)" }}
            className="group relative rounded-2xl border border-white/[0.06] bg-white/[0.02] p-5 shadow-sm transition-all hover:border-white/[0.12] hover:shadow-xl"
        >
            <div className="mb-3 flex items-start justify-between">
                <div className="flex items-center gap-2">
                    <span className={`inline-flex rounded-md border px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wider ${priorityColor(ticket.priority || 'Low')}`}>
                        {ticket.priority || 'Low'}
                    </span>
                    <span className="text-[10px] font-medium text-zinc-500">{timeAgo(ticket.created_at)}</span>
                </div>
                <div className="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                    <button
                        onClick={onEdit}
                        className="flex h-7 w-7 items-center justify-center rounded-lg bg-white/10 text-zinc-400 hover:bg-white hover:text-black transition-all"
                    >
                        <Pencil className="h-3 w-3" />
                    </button>
                    <button
                        onClick={onDelete}
                        className="flex h-7 w-7 items-center justify-center rounded-lg bg-red-500/10 text-red-500 hover:bg-red-500 hover:text-white transition-all"
                    >
                        <Trash2 className="h-3 w-3" />
                    </button>
                </div>
            </div>

            <h4 className="text-[15px] font-bold leading-snug text-white/90 group-hover:text-white">
                {ticket.title}
            </h4>
            <p className="mt-2 line-clamp-2 text-xs leading-relaxed text-zinc-500 group-hover:text-zinc-400">
                {ticket.description}
            </p>

            <div className="mt-4 flex flex-wrap gap-1.5">
                {ticket.category && (
                    <span className={`rounded-lg border px-2 py-1 text-[10px] font-bold ${categoryColor(ticket.category)}`}>
                        {ticket.category}
                    </span>
                )}
                <span className="rounded-lg bg-white/[0.05] px-2 py-1 text-[10px] font-medium text-zinc-400">
                    {ticket.customer_email.split('@')[0]}
                </span>
            </div>

            {ticket.ai_confidence !== null && (
                <div className="mt-5">
                    <div className="flex items-center justify-between text-[9px] font-bold uppercase tracking-widest text-zinc-600">
                        <span>AI Confidence</span>
                        <span>{(ticket.ai_confidence * 100).toFixed(0)}%</span>
                    </div>
                    <div className="mt-1.5 h-1 w-full overflow-hidden rounded-full bg-white/[0.05]">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${(ticket.ai_confidence * 100).toFixed(0)}%` }}
                            className="h-full bg-gradient-to-r from-indigo-500/50 to-indigo-400"
                        />
                    </div>
                </div>
            )}

            <div className="mt-5 flex items-center justify-between gap-4 border-t border-white/[0.05] pt-4">
                <StatusDropdown
                    ticket={ticket}
                    onUpdate={onUpdateStatus}
                    isUpdating={isUpdating}
                />
                <button className="text-zinc-600 hover:text-white transition-colors">
                    <MoreHorizontal className="h-4 w-4" />
                </button>
            </div>
        </motion.div>
    );
}

// ── Table View ──────────────────────────────

function TableView({
    tickets,
    updatingId,
    onUpdateStatus,
    onEdit,
    onDelete
}: {
    tickets: Ticket[],
    updatingId: string | null,
    onUpdateStatus: (id: string, s: TicketStatus) => void,
    onEdit: (t: Ticket) => void,
    onDelete: (t: Ticket) => void
}) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="overflow-hidden rounded-2xl border border-white/[0.06] bg-white/[0.01] shadow-2xl"
        >
            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                    <thead>
                        <tr className="border-b border-white/[0.06] bg-white/[0.02]">
                            <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-zinc-500">Ticket</th>
                            <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-zinc-500">Status</th>
                            <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-zinc-500">Category</th>
                            <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-zinc-500">Created</th>
                            <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-zinc-500 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/[0.04]">
                        {tickets.map((t) => (
                            <tr key={t.id} className="transition-colors hover:bg-white/[0.02]">
                                <td className="px-6 py-5">
                                    <div className="flex flex-col">
                                        <span className="font-bold text-white/90">{t.title}</span>
                                        <span className="mt-0.5 text-xs text-zinc-500">{t.customer_email}</span>
                                    </div>
                                </td>
                                <td className="px-6 py-5">
                                    <div className="flex items-center gap-2">
                                        <div className={`h-1.5 w-1.5 rounded-full ${t.status === 'Open' ? 'bg-blue-500' : t.status === 'In Progress' ? 'bg-amber-500' : 'bg-emerald-500'
                                            }`} />
                                        <span className="text-xs font-bold text-zinc-300">{t.status}</span>
                                    </div>
                                </td>
                                <td className="px-6 py-5">
                                    <span className={`inline-flex rounded-lg border px-2 py-1 text-[10px] font-bold ${categoryColor(t.category || 'General')}`}>
                                        {t.category || "—"}
                                    </span>
                                </td>
                                <td className="px-6 py-5 text-xs text-zinc-500">{timeAgo(t.created_at)}</td>
                                <td className="px-6 py-5">
                                    <div className="flex items-center justify-end gap-2">
                                        <StatusDropdown
                                            ticket={t}
                                            onUpdate={onUpdateStatus}
                                            isUpdating={updatingId === t.id}
                                        />
                                        <button
                                            onClick={() => onEdit(t)}
                                            className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/5 text-zinc-400 hover:bg-white hover:text-black transition-all"
                                        >
                                            <Pencil className="h-3.5 w-3.5" />
                                        </button>
                                        <button
                                            onClick={() => onDelete(t)}
                                            className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-500/10 text-red-500 hover:bg-red-500 hover:text-white transition-all"
                                        >
                                            <Trash2 className="h-3.5 w-3.5" />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </motion.div>
    );
}

// ── Modals ──────────────────────────────────

function TicketModal({
    title,
    onClose,
    onSuccess,
    mode,
    ticket
}: {
    title: string;
    onClose: () => void;
    onSuccess: (t: Ticket) => void;
    mode: 'create' | 'edit';
    ticket?: Ticket;
}) {
    const [formData, setFormData] = useState({
        title: ticket?.title || "",
        description: ticket?.description || "",
        customer_email: ticket?.customer_email || "",
        priority: ticket?.priority || "Low",
        category: ticket?.category || "General",
    });
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        setError("");

        try {
            let res: Ticket;
            if (mode === 'create') {
                res = await ticketsAPI.create({
                    title: formData.title,
                    description: formData.description,
                    customer_email: formData.customer_email,
                });
            } else {
                res = await ticketsAPI.update(ticket!.id, {
                    title: formData.title,
                    description: formData.description,
                    priority: formData.priority as TicketPriority,
                    category: formData.category as TicketCategory,
                });
            }
            onSuccess(res);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Submission failed");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={onClose}
                className="absolute inset-0 bg-black/80 backdrop-blur-sm"
            />
            <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 20 }}
                className="relative w-full max-w-xl overflow-hidden rounded-[2rem] border border-white/[0.1] bg-zinc-900 shadow-2xl"
            >
                <div className="p-8">
                    <div className="mb-8 flex items-center justify-between">
                        <h3 className="text-2xl font-bold tracking-tight">{title}</h3>
                        <button
                            onClick={onClose}
                            className="flex h-10 w-10 items-center justify-center rounded-full bg-white/5 text-zinc-500 hover:bg-white/10 hover:text-white transition-all"
                        >
                            <X className="h-5 w-5" />
                        </button>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-xs font-bold uppercase tracking-widest text-zinc-500">Issue Title</label>
                            <input
                                required
                                value={formData.title}
                                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                placeholder="Short description of the issue"
                                className="w-full rounded-2xl border border-white/[0.08] bg-white/[0.02] px-5 py-4 text-sm text-white focus:border-indigo-500 focus:outline-none"
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs font-bold uppercase tracking-widest text-zinc-500">Full Description</label>
                            <textarea
                                required
                                rows={4}
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                placeholder="Detailed details about the problem..."
                                className="w-full resize-none rounded-2xl border border-white/[0.08] bg-white/[0.02] px-5 py-4 text-sm text-white focus:border-indigo-500 focus:outline-none"
                            />
                        </div>

                        {mode === 'create' && (
                            <div className="space-y-2">
                                <label className="text-xs font-bold uppercase tracking-widest text-zinc-500">Customer Email</label>
                                <input
                                    required
                                    type="email"
                                    value={formData.customer_email}
                                    onChange={(e) => setFormData({ ...formData, customer_email: e.target.value })}
                                    placeholder="customer@example.com"
                                    className="w-full rounded-2xl border border-white/[0.08] bg-white/[0.02] px-5 py-4 text-sm text-white focus:border-indigo-500 focus:outline-none"
                                />
                            </div>
                        )}

                        {mode === 'edit' && (
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-xs font-bold uppercase tracking-widest text-zinc-500">Severity</label>
                                    <select
                                        value={formData.priority}
                                        onChange={(e) => setFormData({ ...formData, priority: e.target.value as TicketPriority })}
                                        className="w-full rounded-2xl border border-white/[0.08] bg-white/[0.02] px-5 py-4 text-sm text-white focus:border-indigo-500 focus:outline-none"
                                    >
                                        <option value="High">High</option>
                                        <option value="Medium">Medium</option>
                                        <option value="Low">Low</option>
                                    </select>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-xs font-bold uppercase tracking-widest text-zinc-500">Category</label>
                                    <select
                                        value={formData.category}
                                        onChange={(e) => setFormData({ ...formData, category: e.target.value as TicketCategory })}
                                        className="w-full rounded-2xl border border-white/[0.08] bg-white/[0.02] px-5 py-4 text-sm text-white focus:border-indigo-500 focus:outline-none"
                                    >
                                        <option value="Billing">Billing</option>
                                        <option value="Technical Bug">Technical Bug</option>
                                        <option value="Feature Request">Feature Request</option>
                                        <option value="Account">Account</option>
                                        <option value="General">General</option>
                                    </select>
                                </div>
                            </div>
                        )}

                        {error && (
                            <p className="text-sm font-medium text-red-400">{error}</p>
                        )}

                        <div className="flex gap-4 pt-4">
                            <button
                                type="button"
                                onClick={onClose}
                                className="flex-1 rounded-2xl border border-white/[0.08] bg-white/5 py-4 text-sm font-bold transition-all hover:bg-white/10"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={isSubmitting}
                                className="flex-1 rounded-2xl bg-indigo-500 py-4 text-sm font-bold text-white shadow-lg shadow-indigo-500/20 transition-all hover:bg-indigo-600 disabled:opacity-50"
                            >
                                {isSubmitting ? "Syncing..." : mode === 'create' ? "Launch Ticket" : "Apply Changes"}
                            </button>
                        </div>
                    </form>
                </div>
            </motion.div>
        </div>
    );
}

function DeleteConfirmationModal({ ticket, onClose, onConfirm }: { ticket: Ticket, onClose: () => void, onConfirm: () => void }) {
    const [isDeleting, setIsDeleting] = useState(false);

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={onClose} className="absolute inset-0 bg-black/80 backdrop-blur-sm" />
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }}
                className="relative w-full max-w-sm overflow-hidden rounded-[2rem] border border-white/[0.1] bg-zinc-900 p-8 shadow-2xl text-center"
            >
                <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-red-500/10 text-red-500">
                    <Trash2 className="h-8 w-8" />
                </div>
                <h3 className="text-xl font-bold tracking-tight">Destructive Action</h3>
                <p className="mt-2 text-sm leading-relaxed text-zinc-500">
                    Are you sure you want to delete <span className="text-white font-bold">{ticket.title}</span>? This cannot be undone.
                </p>
                <div className="mt-8 flex flex-col gap-3">
                    <button
                        onClick={async () => {
                            setIsDeleting(true);
                            await onConfirm();
                            setIsDeleting(false);
                        }}
                        disabled={isDeleting}
                        className="w-full rounded-2xl bg-red-500 py-4 text-sm font-bold text-white shadow-lg shadow-red-500/20 transition-all hover:bg-red-600 disabled:opacity-50"
                    >
                        {isDeleting ? "Deleting..." : "Delete Permanently"}
                    </button>
                    <button
                        onClick={onClose}
                        className="w-full rounded-2xl border border-white/[0.08] bg-white/5 py-4 text-sm font-bold transition-all hover:bg-white/10"
                    >
                        Keep Ticket
                    </button>
                </div>
            </motion.div>
        </div>
    );
}

// ── Status Dropdown ──────────────────────────

function StatusDropdown({
    ticket,
    onUpdate,
    isUpdating,
}: {
    ticket: Ticket;
    onUpdate: (id: string, status: TicketStatus) => void;
    isUpdating: boolean;
}) {
    const transitions: Record<TicketStatus, TicketStatus[]> = {
        Open: ["In Progress", "Resolved"],
        "In Progress": ["Resolved", "Open"],
        Resolved: ["Open"],
    };

    const available = transitions[ticket.status] || [];

    return (
        <div className="relative group/select">
            <select
                value=""
                disabled={isUpdating}
                onChange={(e) => {
                    if (e.target.value) onUpdate(ticket.id, e.target.value as TicketStatus);
                }}
                className="appearance-none rounded-xl border border-white/[0.08] bg-white/[0.04] px-4 py-2 text-[11px] font-bold text-zinc-400 transition-all hover:border-white/[0.15] hover:bg-white/[0.08] focus:outline-none disabled:opacity-50"
            >
                <option value="">Move to...</option>
                {available.map((s) => (
                    <option key={s} value={s} className="bg-zinc-900 text-white">
                        {s}
                    </option>
                ))}
            </select>
            {isUpdating && (
                <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    <div className="h-3 w-3 animate-spin rounded-full border border-indigo-500 border-t-transparent" />
                </div>
            )}
        </div>
    );
}
