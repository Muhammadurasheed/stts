/* ============================================
 * STTS TypeScript Types
 * ============================================ */

// ── Ticket Types ─────────────────────────────

export type TicketStatus = "Open" | "In Progress" | "Resolved";
export type TicketPriority = "High" | "Medium" | "Low";
export type TicketCategory =
  | "Billing"
  | "Technical Bug"
  | "Feature Request"
  | "Account"
  | "General";

export interface Ticket {
  id: string;
  title: string;
  description: string;
  customer_email: string;
  status: TicketStatus;
  priority: TicketPriority | null;
  category: TicketCategory | null;
  ai_confidence: number | null;
  ai_reasoning: string | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
}

export interface TicketCreatePayload {
  title: string;
  description: string;
  customer_email: string;
}

export interface TicketStatusUpdatePayload {
  status: TicketStatus;
}

export interface TicketUpdatePayload {
  title?: string;
  description?: string;
  priority?: TicketPriority;
  category?: TicketCategory;
}

export interface TicketListResponse {
  items: Ticket[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ── Auth Types ────────────────────────────────

export interface Agent {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  google_id?: string;
  picture_url?: string;
  created_at: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  agent: Agent;
}

// ── API Error ─────────────────────────────────

export interface APIError {
  error: boolean;
  message: string;
  status_code: number;
}
