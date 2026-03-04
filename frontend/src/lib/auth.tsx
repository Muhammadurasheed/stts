/* ============================================
 * STTS Auth Context
 * ============================================
 * Provides auth state and actions across the app.
 */

"use client";

import {
    createContext,
    useContext,
    useEffect,
    useState,
    useCallback,
    type ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import type { Agent, LoginPayload } from "@/types";
import { authAPI } from "@/lib/api";

interface AuthContextType {
    agent: Agent | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    login: (data: LoginPayload) => Promise<void>;
    googleLogin: (token: string) => Promise<void>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [agent, setAgent] = useState<Agent | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    // Check for existing token on mount
    useEffect(() => {
        const token = localStorage.getItem("stts_token");
        const cachedAgent = localStorage.getItem("stts_agent");

        if (cachedAgent) {
            try {
                setAgent(JSON.parse(cachedAgent));
            } catch (e) {
                localStorage.removeItem("stts_agent");
            }
        }

        if (token) {
            authAPI
                .getMe()
                .then((freshAgent) => {
                    setAgent(freshAgent);
                    localStorage.setItem("stts_agent", JSON.stringify(freshAgent));
                })
                .catch(() => {
                    localStorage.removeItem("stts_token");
                    localStorage.removeItem("stts_agent");
                    setAgent(null);
                })
                .finally(() => setIsLoading(false));
        } else {
            setIsLoading(false);
        }
    }, []);

    const login = useCallback(
        async (data: LoginPayload) => {
            const response = await authAPI.login(data);
            localStorage.setItem("stts_token", response.access_token);
            localStorage.setItem("stts_agent", JSON.stringify(response.agent));
            setAgent(response.agent);
            router.push("/dashboard");
        },
        [router]
    );

    const googleLogin = useCallback(
        async (token: string) => {
            const response = await authAPI.googleLogin(token);
            localStorage.setItem("stts_token", response.access_token);
            localStorage.setItem("stts_agent", JSON.stringify(response.agent));
            setAgent(response.agent);
            router.push("/dashboard");
        },
        [router]
    );

    const logout = useCallback(() => {
        localStorage.removeItem("stts_token");
        localStorage.removeItem("stts_agent");
        setAgent(null);
        router.push("/login");
    }, [router]);

    return (
        <AuthContext.Provider
            value={{
                agent,
                isLoading,
                isAuthenticated: !!agent,
                login,
                googleLogin,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error("useAuth must be used within AuthProvider");
    return ctx;
}
