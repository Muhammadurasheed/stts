"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function HomePage() {
  const [mounted, setMounted] = useState(false);
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();

  useEffect(() => setMounted(true), []);

  // Auto-redirect logged-in users to dashboard
  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.push("/dashboard");
    }
  }, [authLoading, isAuthenticated, router]);

  return (
    <div className="relative min-h-screen overflow-hidden bg-zinc-950">
      {/* ── Gradient orbs ───────────────────── */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-32 -top-32 h-[500px] w-[500px] rounded-full bg-indigo-600/10 blur-[120px]" />
        <div className="absolute -right-32 top-1/3 h-[400px] w-[400px] rounded-full bg-violet-600/10 blur-[120px]" />
        <div className="absolute bottom-0 left-1/3 h-[350px] w-[350px] rounded-full bg-sky-600/8 blur-[100px]" />
      </div>

      {/* ── Navigation ─────────────────────── */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-6">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 text-sm font-bold">
            ST
          </div>
          <span className="text-lg font-semibold tracking-tight">STTS</span>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/login"
            className="rounded-lg px-5 py-2.5 text-sm font-medium text-zinc-400 transition-colors hover:text-white"
          >
            Agent Login
          </Link>
          <Link
            href="/submit"
            className="rounded-lg bg-gradient-to-r from-indigo-500 to-violet-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition-all hover:shadow-indigo-500/40 hover:brightness-110"
          >
            Submit Ticket
          </Link>
        </div>
      </nav>

      {/* ── Hero ────────────────────────────── */}
      <main className="relative z-10 flex flex-col items-center px-6 pt-24 text-center">
        <div
          className={`transition-all duration-700 ${mounted ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
            }`}
        >
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-indigo-500/20 bg-indigo-500/10 px-4 py-1.5 text-xs font-medium text-indigo-400">
            <span className="h-1.5 w-1.5 rounded-full bg-indigo-400 animate-pulse" />
            Powered by Google Gemini AI
          </div>

          <h1 className="mx-auto max-w-4xl text-5xl font-extrabold leading-tight tracking-tight sm:text-6xl lg:text-7xl">
            <span className="bg-gradient-to-r from-white via-zinc-200 to-zinc-400 bg-clip-text text-transparent">
              Smart Triage
            </span>
            <br />
            <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-purple-400 bg-clip-text text-transparent">
              Ticketing System
            </span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-zinc-400">
            Submit support tickets and get instant AI-powered classification.
            Our intelligent triage system categorizes and prioritizes your
            requests so the right team responds faster.
          </p>
        </div>

        {/* ── CTA ──────────────────────────── */}
        <div
          className={`mt-10 flex items-center gap-4 transition-all delay-200 duration-700 ${mounted ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
            }`}
        >
          <Link
            href="/submit"
            className="group relative rounded-xl bg-gradient-to-r from-indigo-500 to-violet-600 px-8 py-4 text-base font-semibold text-white shadow-2xl shadow-indigo-500/25 transition-all hover:shadow-indigo-500/40 hover:brightness-110"
          >
            Submit a Ticket
            <span className="ml-2 inline-block transition-transform group-hover:translate-x-1">
              →
            </span>
          </Link>
          <Link
            href="/login"
            className="rounded-xl border border-zinc-700/50 bg-zinc-900/50 px-8 py-4 text-base font-medium text-zinc-300 transition-all hover:border-zinc-600 hover:bg-zinc-800/50 hover:text-white"
          >
            Agent Dashboard
          </Link>
        </div>

        {/* ── Feature Cards ────────────────── */}
        <div
          className={`mt-24 grid max-w-5xl grid-cols-1 gap-6 sm:grid-cols-3 transition-all delay-500 duration-700 ${mounted ? "translate-y-0 opacity-100" : "translate-y-12 opacity-0"
            }`}
        >
          {[
            {
              icon: "🤖",
              title: "AI Triage",
              desc: "Gemini classifies tickets by category and priority in real-time",
            },
            {
              icon: "⚡",
              title: "Instant Response",
              desc: "Tickets are triaged within seconds of submission",
            },
            {
              icon: "🛡️",
              title: "Resilient",
              desc: "Circuit breaker + retry ensures reliability even during outages",
            },
          ].map((f) => (
            <div
              key={f.title}
              className="glass group rounded-2xl p-6 transition-all hover:bg-white/[0.05] hover:border-indigo-500/20"
            >
              <div className="mb-3 text-3xl">{f.icon}</div>
              <h3 className="text-base font-semibold text-white">{f.title}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-zinc-400">{f.desc}</p>
            </div>
          ))}
        </div>
      </main>

      {/* ── Footer ─────────────────────────── */}
      <footer className="relative z-10 mt-32 border-t border-zinc-800/50 px-8 py-6 text-center text-xs text-zinc-600">
        STTS — Built with FastAPI, Next.js & Google Gemini ·{" "}
        <span className="text-zinc-500">Codematic Assessment</span>
      </footer>
    </div>
  );
}
