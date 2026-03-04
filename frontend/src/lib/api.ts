/* ============================================
 * STTS API Client
 * ============================================
 * Centralized HTTP client for all backend calls.
 */

import type {
    Ticket,
    TicketCreatePayload,
    TicketListResponse,
    TicketStatusUpdatePayload,
    TicketUpdatePayload,
    TokenResponse,
    LoginPayload,
    RegisterPayload,
    Agent,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_V1 = `${API_BASE}/api/v1`;

// ── Helper ────────────────────────────────────

function getAuthHeaders(): HeadersInit {
    if (typeof window === "undefined") return {};
    const token = localStorage.getItem("stts_token");
    if (!token) return {};
    return { Authorization: `Bearer ${token}` };
}

async function handleResponse<T>(res: Response): Promise<T> {
    if (!res.ok) {
        const body = await res.json().catch(() => ({ message: "Request failed" }));
        throw new Error(body.message || `HTTP ${res.status}`);
    }
    return res.json();
}

// ── Auth API ──────────────────────────────────

export const authAPI = {
    async register(data: RegisterPayload): Promise<Agent> {
        const res = await fetch(`${API_V1}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        return handleResponse<Agent>(res);
    },

    async login(data: LoginPayload): Promise<TokenResponse> {
        const res = await fetch(`${API_V1}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        return handleResponse<TokenResponse>(res);
    },

    async googleLogin(token: string): Promise<TokenResponse> {
        const res = await fetch(`${API_V1}/auth/google`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token }),
        });
        return handleResponse<TokenResponse>(res);
    },

    async getMe(): Promise<Agent> {
        const res = await fetch(`${API_V1}/auth/me`, {
            headers: { ...getAuthHeaders() },
        });
        return handleResponse<Agent>(res);
    },
};

// ── Tickets API ───────────────────────────────

export const ticketsAPI = {
    async create(data: TicketCreatePayload): Promise<Ticket> {
        const res = await fetch(`${API_V1}/tickets`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        return handleResponse<Ticket>(res);
    },

    async list(params?: {
        page?: number;
        page_size?: number;
        status?: string;
        priority?: string;
    }): Promise<TicketListResponse> {
        const query = new URLSearchParams();
        if (params?.page) query.set("page", String(params.page));
        if (params?.page_size) query.set("page_size", String(params.page_size));
        if (params?.status) query.set("status", params.status);
        if (params?.priority) query.set("priority", params.priority);

        const res = await fetch(`${API_V1}/tickets?${query.toString()}`, {
            headers: { ...getAuthHeaders() },
        });
        return handleResponse<TicketListResponse>(res);
    },

    async getById(id: string): Promise<Ticket> {
        const res = await fetch(`${API_V1}/tickets/${id}`, {
            headers: { ...getAuthHeaders() },
        });
        return handleResponse<Ticket>(res);
    },

    async updateStatus(id: string, data: TicketStatusUpdatePayload): Promise<Ticket> {
        const res = await fetch(`${API_V1}/tickets/${id}/status`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json", ...getAuthHeaders() },
            body: JSON.stringify(data),
        });
        return handleResponse<Ticket>(res);
    },

    async update(id: string, data: TicketUpdatePayload): Promise<Ticket> {
        const res = await fetch(`${API_V1}/tickets/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json", ...getAuthHeaders() },
            body: JSON.stringify(data),
        });
        return handleResponse<Ticket>(res);
    },

    async delete(id: string): Promise<void> {
        const res = await fetch(`${API_V1}/tickets/${id}`, {
            method: "DELETE",
            headers: { ...getAuthHeaders() },
        });
        if (!res.ok) {
            const body = await res.json().catch(() => ({ message: "Delete failed" }));
            throw new Error(body.message || `HTTP ${res.status}`);
        }
    },
};
