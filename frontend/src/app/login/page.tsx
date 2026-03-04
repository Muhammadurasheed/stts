"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth";
import { GoogleLogin } from "@react-oauth/google";
import AuthLayout from "@/components/auth/AuthLayout";

export default function LoginPage() {
    const { login, googleLogin } = useAuth();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setIsLoading(true);
        try {
            await login({ email, password });
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : "Login failed");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <AuthLayout
            title="Welcome back"
            subtitle="Please enter your details to sign in"
            type="login"
        >
            <div className="space-y-6">
                <div className="flex justify-center">
                    <GoogleLogin
                        onSuccess={(credentialResponse) => {
                            if (credentialResponse.credential) {
                                googleLogin(credentialResponse.credential);
                            }
                        }}
                        onError={() => {
                            setError("Google Login Failed");
                        }}
                        theme="filled_black"
                        shape="pill"
                        size="large"
                        text="signin_with"
                        width="100%"
                    />
                </div>

                <div className="relative flex items-center py-2">
                    <div className="flex-grow border-t border-zinc-800"></div>
                    <span className="mx-4 flex-shrink text-[10px] font-bold uppercase tracking-widest text-zinc-600">
                        Or use email
                    </span>
                    <div className="flex-grow border-t border-zinc-800"></div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {error && (
                        <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
                            {error}
                        </div>
                    )}

                    <div>
                        <label htmlFor="login-email" className="mb-2 block text-xs font-semibold uppercase tracking-wider text-zinc-500">
                            Email address
                        </label>
                        <input
                            id="login-email"
                            type="email"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="agent@stts.com"
                            className="w-full rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm text-white placeholder-zinc-700 transition-all focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 focus:outline-none"
                        />
                    </div>

                    <div>
                        <label htmlFor="login-password" className="mb-2 block text-xs font-semibold uppercase tracking-wider text-zinc-500">
                            Password
                        </label>
                        <div className="relative">
                            <input
                                id="login-password"
                                type={showPassword ? "text" : "password"}
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="••••••••"
                                className="w-full rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 pr-12 text-sm text-white placeholder-zinc-700 transition-all focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 focus:outline-none"
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-4 top-1/2 -translate-y-1/2 text-zinc-600 transition-colors hover:text-zinc-400"
                            >
                                {showPassword ? (
                                    <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" /></svg>
                                ) : (
                                    <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.036 12.322a1.012 1.012 0 010-.644C3.397 7.051 7.243 4.5 12 4.5c4.757 0 8.603 2.551 9.964 7.178.07.242.07.495 0 .737C20.603 16.949 16.757 19.5 12 19.5c-4.757 0-8.603-2.551-9.964-7.178z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                                )}
                            </button>
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="group relative w-full overflow-hidden rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 py-3 text-sm font-bold text-white shadow-xl shadow-indigo-500/20 transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
                    >
                        <span className="relative z-10">{isLoading ? "Signing in..." : "Sign In"}</span>
                        <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/10 to-transparent transition-transform group-hover:translate-x-full duration-1000" />
                    </button>
                </form>
            </div>
        </AuthLayout>
    );
}
