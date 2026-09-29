export type TransactionType = "income" | "expense";

export interface Income {
  id: number;
  title: string;
  amount: string | number;
  category: string;
  description: string;
  income_date: string;
  created_at: string;
  updated_at: string;
}

export interface Expense {
  id: number;
  title: string;
  amount: string | number;
  category: string;
  description: string;
  expense_date: string;
  created_at: string;
  updated_at: string;
}

export interface IncomeInput {
  title: string;
  amount: number;
  category: string;
  description: string;
  income_date: string;
}

export interface ExpenseInput {
  title: string;
  amount: number;
  category: string;
  description: string;
  expense_date: string;
}

export interface AuthUser {
  id?: string;
  email?: string;
  user_metadata?: Record<string, unknown>;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: AuthUser;
}

export interface ChatResponse {
  response: string;
}

export interface ImportResponse {
  message: string;
  total_transactions: number;
  expenses_created: number;
  income_created: number;
}

export interface ApiError {
  detail?: string | Array<{ loc?: unknown[]; msg?: string; type?: string; input?: unknown; ctx?: unknown }>;
}