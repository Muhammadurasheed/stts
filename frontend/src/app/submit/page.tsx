"use client";

import { useState } from "react";
import Link from "next/link";
import { ticketsAPI } from "@/lib/api";
import type { Ticket } from "@/types";

export default function SubmitTicketPage() {
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [email, setEmail] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitted, setSubmitted] = useState<Ticket | null>(null);
    const [error, setError] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setIsSubmitting(true);

        try {
            const ticket = await ticketsAPI.create({
                title,
                description,
                customer_email: email,
            });
            setSubmitted(ticket);
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : "Failed to submit ticket");
        } finally {
            setIsSubmitting(false);
        }
    };

    // ── Success State ──────────────────────────
    if (submitted) {
        return (
            <div className="relative min-h-screen bg-zinc-950">
                <div className="pointer-events-none absolute inset-0">
                    <div className="absolute -left-32 top-0 h-[400px] w-[400px] rounded-full bg-emerald-600/10 blur-[120px]" />
                </div>

                <nav className="relative z-10 flex items-center gap-3 px-8 py-6">
                    <Link href="/" className="flex items-center gap-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 text-sm font-bold">
                            ST
                        </div>
                        <span className="text-lg font-semibold tracking-tight">STTS</span>
                    </Link>
                </nav>

                <main className="relative z-10 mx-auto max-w-2xl px-6 pt-16">
                    <div className="animate-slide-up rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-10 text-center">
                        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-500/15">
                            <svg className="h-8 w-8 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                            </svg>
                        </div>

                        <h1 className="text-2xl font-bold text-white">Ticket Submitted!</h1>
                        <p className="mt-2 text-zinc-400">Your ticket has been received and triaged by our AI.</p>

                        <div className="mt-8 space-y-4 text-left">
                            <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-5">
                                <div className="flex items-center justify-between">
                                    <span className="text-xs font-medium text-zinc-500">TICKET ID</span>
                                    <span className="font-mono text-xs text-zinc-400">{submitted.id}</span>
                                </div>
                                <h3 className="mt-2 font-semibold text-white">{submitted.title}</h3>

                                <div className="mt-4 flex flex-wrap items-center gap-2">
                                    {submitted.category && (
                                        <span className="rounded-full border border-violet-500/30 bg-violet-500/15 px-3 py-1 text-xs font-medium text-violet-400">
                                            {submitted.category}
                                        </span>
                                    )}
                                    {submitted.priority && (
                                        <span
                                            className={`rounded-full border px-3 py-1 text-xs font-medium ${submitted.priority === "High"
                                                ? "border-red-500/30 bg-red-500/15 text-red-400"
                                                : submitted.priority === "Medium"
                                                    ? "border-amber-500/30 bg-amber-500/15 text-amber-400"
                                                    : "border-emerald-500/30 bg-emerald-500/15 text-emerald-400"
                                                }`}
                                        >
                                            {submitted.priority} Priority
                                        </span>
                                    )}
                                    <Link
                                        href="/dashboard"
                                        className="group flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-3 py-1 text-[11px] font-bold uppercase tracking-wider text-blue-400 transition-all hover:border-blue-400/50 hover:bg-blue-400/20"
                                    >
                                        <span className="relative flex h-2 w-2">
                                            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-blue-400 opacity-75"></span>
                                            <span className="relative inline-flex h-2 w-2 rounded-full bg-blue-500"></span>
                                        </span>
                                        {submitted.status} — View in Dashboard
                                        <svg className="h-3 w-3 transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                        </svg>
                                    </Link>
                                </div>

                                {submitted.ai_reasoning && (
                                    <div className="mt-4 rounded-lg border border-indigo-500/15 bg-indigo-500/5 p-3">
                                        <span className="text-[10px] font-semibold uppercase tracking-wider text-indigo-400">
                                            AI Reasoning
                                        </span>
                                        <p className="mt-1 text-sm text-zinc-300">{submitted.ai_reasoning}</p>
                                        {submitted.ai_confidence !== null && (
                                            <div className="mt-2 flex items-center gap-2">
                                                <div className="h-1.5 flex-1 rounded-full bg-zinc-800">
                                                    <div
                                                        className="h-1.5 rounded-full bg-gradient-to-r from-indigo-500 to-violet-500"
                                                        style={{ width: `${(submitted.ai_confidence * 100).toFixed(0)}%` }}
                                                    />
                                                </div>
                                                <span className="text-xs text-zinc-500">
                                                    {(submitted.ai_confidence * 100).toFixed(0)}%
                                                </span>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="mt-8 flex justify-center gap-3">
                            <button
                                onClick={() => {
                                    setSubmitted(null);
                                    setTitle("");
                                    setDescription("");
                                    setEmail("");
                                }}
                                className="rounded-lg border border-zinc-700 bg-zinc-800/50 px-6 py-2.5 text-sm font-medium text-zinc-300 transition-all hover:bg-zinc-700/50"
                            >
                                Submit Another
                            </button>
                            <Link
                                href="/"
                                className="rounded-lg bg-gradient-to-r from-indigo-500 to-violet-600 px-6 py-2.5 text-sm font-semibold text-white transition-all hover:brightness-110"
                            >
                                Back Home
                            </Link>
                        </div>
                    </div>
                </main>
            </div>
        );
    }

    // ── Form State ─────────────────────────────
    return (
        <div className="relative min-h-screen bg-zinc-950">
            <div className="pointer-events-none absolute inset-0">
                <div className="absolute -right-32 -top-32 h-[400px] w-[400px] rounded-full bg-indigo-600/10 blur-[120px]" />
                <div className="absolute -left-20 bottom-0 h-[300px] w-[300px] rounded-full bg-violet-600/8 blur-[100px]" />
            </div>

            <nav className="relative z-10 flex items-center gap-3 px-8 py-6">
                <Link href="/" className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 text-sm font-bold">
                        ST
                    </div>
                    <span className="text-lg font-semibold tracking-tight">STTS</span>
                </Link>
            </nav>

            <main className="relative z-10 mx-auto max-w-2xl px-6 pt-12">
                <div className="animate-fade-in">
                    <h1 className="text-3xl font-bold tracking-tight text-white">Submit a Ticket</h1>
                    <p className="mt-2 text-zinc-400">
                        Describe your issue and our AI will classify it instantly.
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="animate-slide-up mt-8 space-y-6">
                    {error && (
                        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
                            {error}
                        </div>
                    )}

                    <div>
                        <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-zinc-300">
                            Your Email
                        </label>
                        <input
                            id="email"
                            type="email"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="you@company.com"
                            className="w-full rounded-xl border border-zinc-800 bg-zinc-900/50 px-4 py-3 text-white placeholder-zinc-600 transition-colors focus:border-indigo-500/50 focus:bg-zinc-900 focus:outline-none"
                        />
                    </div>

                    <div>
                        <label htmlFor="title" className="mb-1.5 block text-sm font-medium text-zinc-300">
                            Title
                        </label>
                        <input
                            id="title"
                            type="text"
                            required
                            minLength={3}
                            maxLength={200}
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            placeholder="Brief summary of your issue"
                            className="w-full rounded-xl border border-zinc-800 bg-zinc-900/50 px-4 py-3 text-white placeholder-zinc-600 transition-colors focus:border-indigo-500/50 focus:bg-zinc-900 focus:outline-none"
                        />
                    </div>

                    <div>
                        <label htmlFor="description" className="mb-1.5 block text-sm font-medium text-zinc-300">
                            Description
                        </label>
                        <textarea
                            id="description"
                            required
                            minLength={10}
                            maxLength={5000}
                            rows={6}
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="Describe your issue in detail — the more context, the better our AI can classify it..."
                            className="w-full resize-none rounded-xl border border-zinc-800 bg-zinc-900/50 px-4 py-3 text-white placeholder-zinc-600 transition-colors focus:border-indigo-500/50 focus:bg-zinc-900 focus:outline-none"
                        />
                        <p className="mt-1 text-xs text-zinc-600">{description.length} / 5000 characters</p>
                    </div>

                    <button
                        type="submit"
                        disabled={isSubmitting}
                        className="w-full rounded-xl bg-gradient-to-r from-indigo-500 to-violet-600 px-6 py-3.5 text-base font-semibold text-white shadow-lg shadow-indigo-500/25 transition-all hover:shadow-indigo-500/40 hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                        {isSubmitting ? (
                            <span className="flex items-center justify-center gap-2">
                                <svg className="h-5 w-5 animate-spin" viewBox="0 0 24 24" fill="none">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                </svg>
                                Submitting & Analyzing...
                            </span>
                        ) : (
                            "Submit Ticket"
                        )}
                    </button>
                </form>
            </main>
        </div>
    );
}
