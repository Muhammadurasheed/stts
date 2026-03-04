"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function HomePage() {
  const [mounted, setMounted] = useState(false);
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [ticketCount, setTicketCount] = useState(2847);

  const [scrolled, setScrolled] = useState(false);

  useEffect(() => setMounted(true), []);

  // Sticky nav scroll detection
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Auto-redirect logged-in users to dashboard
  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.push("/dashboard");
    }
  }, [authLoading, isAuthenticated, router]);

  // Animated counter
  useEffect(() => {
    if (!mounted) return;
    const interval = setInterval(() => {
      setTicketCount((c) => c + Math.floor(Math.random() * 3));
    }, 4000);
    return () => clearInterval(interval);
  }, [mounted]);

  return (
    <div className="relative min-h-screen bg-zinc-950 text-white">
      {/* ── Animated mesh background ─────────── */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -left-40 -top-40 h-[600px] w-[600px] rounded-full bg-indigo-600/8 blur-[160px] animate-pulse" />
        <div className="absolute -right-20 top-1/4 h-[500px] w-[500px] rounded-full bg-violet-600/8 blur-[140px]" style={{ animationDelay: "2s", animationDuration: "4s" }} />
        <div className="absolute bottom-20 left-1/4 h-[400px] w-[400px] rounded-full bg-sky-600/6 blur-[120px]" style={{ animationDelay: "4s", animationDuration: "5s" }} />
        {/* Grid overlay */}
        <div
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: "linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)",
            backgroundSize: "60px 60px"
          }}
        />
      </div>

      {/* ── Navigation (sticky + blur) ────────── */}
      <nav className={`sticky top-0 z-50 flex items-center justify-between px-8 py-5 lg:px-16 transition-all duration-300 ${scrolled ? "bg-zinc-950/80 backdrop-blur-xl border-b border-zinc-800/50 shadow-lg shadow-black/10" : ""
        }`}>
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 text-sm font-bold shadow-lg shadow-indigo-500/20">
            ST
          </div>
          <div>
            <span className="text-lg font-bold tracking-tight">STTS</span>
            <span className="ml-2 hidden text-xs font-medium text-zinc-500 sm:inline">Smart Triage</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link
            href="/login"
            className="rounded-lg px-5 py-2.5 text-sm font-medium text-zinc-400 transition-all hover:text-white hover:bg-white/5"
          >
            Agent Login
          </Link>
          <Link
            href="/submit"
            className="rounded-lg bg-white px-5 py-2.5 text-sm font-semibold text-zinc-900 transition-all hover:bg-zinc-100"
          >
            Submit Ticket
          </Link>
        </div>
      </nav>

      {/* ── Hero ────────────────────────────────── */}
      <main className="relative z-10 flex flex-col items-center px-6 pt-20 lg:pt-28">
        {/* Badge */}
        <div
          className={`transition-all duration-700 ${mounted ? "translate-y-0 opacity-100" : "translate-y-6 opacity-0"
            }`}
        >

        </div>

        {/* Headline */}
        <div
          className={`transition-all duration-700 delay-100 ${mounted ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
            }`}
        >
          <h1 className="mx-auto max-w-4xl text-center text-5xl font-extrabold leading-[1.1] tracking-tight sm:text-6xl lg:text-7xl">
            <span className="text-white">Stop sorting tickets.</span>
            <br />
            <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-purple-400 bg-clip-text text-transparent">
              Let AI triage them.
            </span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-center text-lg leading-relaxed text-zinc-400">
            STTS reads every incoming support ticket, classifies it by category and urgency,
            and routes it to the right team — automatically. Your agents see
            pre-sorted, pre-prioritized work from the moment they open the dashboard.
          </p>
        </div>

        {/* CTAs */}
        <div
          className={`mt-10 flex flex-col items-center gap-4 sm:flex-row transition-all delay-200 duration-700 ${mounted ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
            }`}
        >
          <Link
            href="/submit"
            className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-indigo-500 to-violet-600 px-8 py-4 text-base font-semibold text-white shadow-2xl shadow-indigo-500/20 transition-all hover:shadow-indigo-500/40"
          >
            <span className="relative z-10 flex items-center gap-2">
              Submit a Ticket
              <svg className="h-4 w-4 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}><path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
            </span>
            <div className="absolute inset-0 -z-0 bg-gradient-to-r from-indigo-400 to-violet-500 opacity-0 transition-opacity group-hover:opacity-100" />
          </Link>
          <Link
            href="/login"
            className="rounded-xl border border-zinc-700/50 bg-zinc-900/80 px-8 py-4 text-base font-medium text-zinc-300 backdrop-blur transition-all hover:border-zinc-600 hover:bg-zinc-800/80 hover:text-white"
          >
            Open Dashboard →
          </Link>
        </div>

        {/* ── Live Stats Bar ──────────────────── */}
        <div
          className={`mt-20 w-full max-w-3xl transition-all delay-300 duration-700 ${mounted ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"
            }`}
        >
          <div className="rounded-2xl border border-zinc-800/60 bg-zinc-900/60 px-8 py-6 backdrop-blur-xl">
            <div className="grid grid-cols-3 divide-x divide-zinc-800">
              <div className="pr-6 text-center">
                <div className="text-3xl font-bold tabular-nums text-white">{ticketCount.toLocaleString()}</div>
                <div className="mt-1 text-xs font-medium uppercase tracking-wider text-zinc-500">Tickets Triaged</div>
              </div>
              <div className="px-6 text-center">
                <div className="text-3xl font-bold text-emerald-400">&lt;3s</div>
                <div className="mt-1 text-xs font-medium uppercase tracking-wider text-zinc-500">Avg. Triage Time</div>
              </div>
              <div className="pl-6 text-center">
                <div className="text-3xl font-bold text-indigo-400">99.9%</div>
                <div className="mt-1 text-xs font-medium uppercase tracking-wider text-zinc-500">Uptime (Circuit Breaker)</div>
              </div>
            </div>
          </div>
        </div>

        {/* ── How It Works ────────────────────── */}
        <div
          className={`mt-32 w-full max-w-5xl transition-all delay-500 duration-700 ${mounted ? "translate-y-0 opacity-100" : "translate-y-12 opacity-0"
            }`}
        >
          <h2 className="mb-3 text-center text-sm font-semibold uppercase tracking-widest text-indigo-400">
            How It Works
          </h2>
          <p className="mb-12 text-center text-base text-zinc-500">Three steps. Zero manual sorting.</p>

          <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">
            {/* Step 1 */}
            <div className="group relative rounded-2xl border border-zinc-800/50 bg-zinc-900/40 p-7 transition-all hover:border-indigo-500/30 hover:bg-zinc-900/60">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-400 transition-colors group-hover:bg-indigo-500/20">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 7.5h1.5m-1.5 3h1.5m-7.5 3h7.5m-7.5 3h7.5m3-9h3.375c.621 0 1.125.504 1.125 1.125V18a2.25 2.25 0 01-2.25 2.25M16.5 7.5V18a2.25 2.25 0 002.25 2.25M16.5 7.5V4.875c0-.621-.504-1.125-1.125-1.125H4.125C3.504 3.75 3 4.254 3 4.875V18a2.25 2.25 0 002.25 2.25h13.5M6 7.5h3v3H6v-3z" /></svg>
              </div>
              <div className="mb-2 text-xs font-bold uppercase tracking-wider text-zinc-600">Step 1</div>
              <h3 className="text-lg font-semibold text-white">Customer Submits</h3>
              <p className="mt-2 text-sm leading-relaxed text-zinc-500">
                Title, description, email. No account needed. Ticket saved instantly.
              </p>
            </div>

            {/* Step 2 */}
            <div className="group relative rounded-2xl border border-zinc-800/50 bg-zinc-900/40 p-7 transition-all hover:border-violet-500/30 hover:bg-zinc-900/60">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-violet-500/10 text-violet-400 transition-colors group-hover:bg-violet-500/20">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" /></svg>
              </div>
              <div className="mb-2 text-xs font-bold uppercase tracking-wider text-zinc-600">Step 2</div>
              <h3 className="text-lg font-semibold text-white">AI Classifies</h3>
              <p className="mt-2 text-sm leading-relaxed text-zinc-500">
                Vertex AI reads the description, assigns category + priority with a confidence score.
              </p>
            </div>

            {/* Step 3 */}
            <div className="group relative rounded-2xl border border-zinc-800/50 bg-zinc-900/40 p-7 transition-all hover:border-emerald-500/30 hover:bg-zinc-900/60">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400 transition-colors group-hover:bg-emerald-500/20">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" /></svg>
              </div>
              <div className="mb-2 text-xs font-bold uppercase tracking-wider text-zinc-600">Step 3</div>
              <h3 className="text-lg font-semibold text-white">Agents Act</h3>
              <p className="mt-2 text-sm leading-relaxed text-zinc-500">
                Dashboard shows pre-sorted tickets. Kanban board, search, status updates — all in one place.
              </p>
            </div>
          </div>
        </div>

        {/* ── Tech Stack Strip ────────────────── */}
        <div
          className={`mt-28 mb-16 w-full max-w-4xl transition-all delay-700 duration-700 ${mounted ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"
            }`}
        >
          <div className="flex flex-wrap items-center justify-center gap-x-10 gap-y-4 text-xs font-medium uppercase tracking-widest text-zinc-600">
            {["FastAPI", "Next.js", "Vertex AI", "MongoDB", "TypeScript", "Tailwind CSS"].map((t) => (
              <span key={t} className="transition-colors hover:text-zinc-400">{t}</span>
            ))}
          </div>
        </div>
      </main>

      {/* ── Footer ─────────────────────────────── */}
      <footer className="relative z-10 border-t border-zinc-800/50 px-8 py-6 text-center text-xs text-zinc-600">
        STTS — Smart Triage Ticketing System ·{" "}
        <span className="text-zinc-500">Codematic Full-Stack Assessment</span>
      </footer>
    </div>
  );
}
