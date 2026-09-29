import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { api, clearToken, hasToken, saveToken } from "./api";
import type { AuthUser } from "./types";

type AuthContextValue = {
  user: AuthUser | null;
  authenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<string>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => {
    const raw = localStorage.getItem("ledger_user");
    return raw ? JSON.parse(raw) : null;
  });

  useEffect(() => {
    if (user) localStorage.setItem("ledger_user", JSON.stringify(user));
    else localStorage.removeItem("ledger_user");
  }, [user]);

  const value = useMemo<AuthContextValue>(() => ({
    user,
    authenticated: hasToken(),
    async login(email, password) {
      const result = await api.login(email, password);
      saveToken(result.access_token);
      setUser(result.user);
    },
    async signup(email, password) {
      return api.signup(email, password);
    },
    logout() {
      clearToken();
      setUser(null);
    }
  }), [user]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}