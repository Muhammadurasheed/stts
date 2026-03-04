import Link from "next/link";
import React from "react";

interface AuthLayoutProps {
    children: React.ReactNode;
    title: string;
    subtitle: string;
    type: "login" | "register";
}

export default function AuthLayout({ children, title, subtitle, type }: AuthLayoutProps) {
    return (
        <div className="flex min-h-screen bg-zinc-950">
            {/* ── Left Side: Marketing/Sidebar ────────────────────────── */}
            <div className="hidden lg:flex lg:w-1/2 relative bg-zinc-900 items-center justify-center p-12 overflow-hidden">
                {/* Animated gradients for depth */}
                <div className="absolute top-0 left-0 w-full h-full">
                    <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-indigo-500/10 blur-[120px] rounded-full animate-pulse" />
                    <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-violet-600/10 blur-[120px] rounded-full animate-pulse delay-1000" />
                </div>

                <div className="relative z-10 max-w-lg text-center lg:text-left">
                    <Link href="/" className="mb-12 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 text-xl font-bold text-white shadow-lg shadow-indigo-500/20">
                        ST
                    </Link>

                    <h2 className="text-4xl font-bold tracking-tight text-white mb-6 leading-tight">
                        The Hub for <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">Smart Triage</span> & Support
                    </h2>

                    <p className="text-lg text-zinc-400 mb-10 leading-relaxed">
                        Revolutionize your customer support with AI-driven ticketing. Automate your triage and focus on what matters most.
                    </p>

                    <div className="space-y-6">
                        <div className="flex items-center gap-4 group">
                            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 group-hover:scale-110 transition-transform">
                                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                            </div>
                            <div>
                                <h4 className="font-semibold text-zinc-200">Lightning Fast Triage</h4>
                                <p className="text-sm text-zinc-500">Tickets categorized in milliseconds by Gemini AI.</p>
                            </div>
                        </div>

                        <div className="flex items-center gap-4 group">
                            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-violet-500/10 border border-violet-500/20 text-violet-400 group-hover:scale-110 transition-transform">
                                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
                            </div>
                            <div>
                                <h4 className="font-semibold text-zinc-200">Data-Driven Insights</h4>
                                <p className="text-sm text-zinc-500">Real-time stats and Kanban boards for your team.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* ── Right Side: Auth Form ───────────────────────────── */}
            <div className="flex flex-1 flex-col justify-center px-6 py-12 lg:px-24">
                <div className="mx-auto w-full max-w-sm">
                    {/* Apple-style back button */}
                    <Link href="/" className="group mb-8 inline-flex items-center gap-1.5 text-sm font-medium text-zinc-500 transition-colors hover:text-white">
                        <svg className="h-4 w-4 transition-transform group-hover:-translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
                        </svg>
                        Back
                    </Link>
                    <div className="lg:hidden mb-8">
                        <Link href="/" className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-500 text-lg font-bold text-white">
                            ST
                        </Link>
                    </div>

                    <div className="mb-10">
                        <h1 className="text-2xl font-bold tracking-tight text-white">{title}</h1>
                        <p className="mt-2 text-sm text-zinc-500 italic">{subtitle}</p>
                    </div>

                    {children}

                    <p className="mt-10 text-center text-sm text-zinc-500">
                        {type === "login" ? (
                            <>
                                Don't have an account?{" "}
                                <Link href="/register" className="font-semibold text-indigo-400 hover:text-indigo-300 transition-colors">
                                    Create one now
                                </Link>
                            </>
                        ) : (
                            <>
                                Already have an account?{" "}
                                <Link href="/login" className="font-semibold text-indigo-400 hover:text-indigo-300 transition-colors">
                                    Sign in
                                </Link>
                            </>
                        )}
                    </p>
                </div>
            </div>
        </div>
    );
}
