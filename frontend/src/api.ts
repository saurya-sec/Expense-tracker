import type {
  AuthResponse, ChatResponse, Expense, ExpenseInput, ImportResponse,
  Income, IncomeInput
} from "./types";

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
const TOKEN_KEY = "ledger_access_token";

export class ApiRequestError extends Error {
  status: number;
  detail: unknown;

  constructor(message: string, status: number, detail?: unknown) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.detail = detail;
  }
}

function token() {
  return localStorage.getItem(TOKEN_KEY);
}

async function parseBody(response: Response): Promise<unknown> {
  const text = await response.text();
  if (!text) return undefined;
  try { return JSON.parse(text); } catch { return text; }
}

async function request<T>(
  path: string,
  options: RequestInit & { auth?: boolean } = {}
): Promise<T> {
  const { auth = false, headers, ...init } = options;
  const merged = new Headers(headers);
  merged.set("Accept", "application/json");
  if (init.body && !(init.body instanceof FormData)) {
    merged.set("Content-Type", "application/json");
  }
  if (auth) {
    const accessToken = token();
    if (!accessToken) throw new ApiRequestError("Authentication required.", 401);
    merged.set("Authorization", `Bearer ${accessToken}`);
  }

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, { ...init, headers: merged });
  } catch (error) {
    throw new ApiRequestError(
      `Cannot reach the API at ${BASE_URL}. Start FastAPI and verify VITE_API_BASE_URL.`,
      0,
      error
    );
  }

  const body = await parseBody(response);
  if (!response.ok) {
    let message = `Request failed (${response.status}).`;
    if (typeof body === "object" && body && "detail" in body) {
      const detail = (body as { detail: unknown }).detail;
      message = Array.isArray(detail)
        ? detail.map((x: any) => x?.msg || JSON.stringify(x)).join(", ")
        : String(detail);
    } else if (typeof body === "string" && body) {
      message = body;
    }
    throw new ApiRequestError(message, response.status, body);
  }
  return body as T;
}

export const api = {
  root: () => request<{ message: string }>("/"),
  dbHealth: () => request<unknown>("/health/db"),

  signup: (email: string, password: string) =>
    request<string>("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password })
    }),

  login: (email: string, password: string) =>
    request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    }),

  listIncome: () => request<Income[]>("/income"),
  getIncome: (id: number) => request<Income>(`/income/${id}`),
  createIncome: (data: IncomeInput) =>
    request<Income>("/income", { method: "POST", body: JSON.stringify(data) }),
  updateIncome: (id: number, data: IncomeInput) =>
    request<Income>(`/income/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteIncome: (id: number) =>
    request<void>(`/income/${id}`, { method: "DELETE" }),

  listExpenses: () => request<Expense[]>("/expenses"),
  getExpense: (id: number) => request<Expense>(`/expenses/${id}`),
  createExpense: (data: ExpenseInput) =>
    request<Expense>("/expenses", { method: "POST", body: JSON.stringify(data) }),
  updateExpense: (id: number, data: ExpenseInput) =>
    request<Expense>(`/expenses/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteExpense: (id: number) =>
    request<void>(`/expenses/${id}`, { method: "DELETE" }),

  chat: (message: string) =>
    request<ChatResponse>("/chat", {
      method: "POST",
      auth: true,
      body: JSON.stringify({ message })
    }),

  uploadEsewa: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<ImportResponse>("/esewa/upload", { method: "POST", body: form });
  },

  uploadStatement: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<unknown>("/statement/upload", { method: "POST", body: form });
  }
};

export function saveToken(accessToken: string) {
  localStorage.setItem(TOKEN_KEY, accessToken);
}
export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}
export function hasToken() {
  return Boolean(token());
}