import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import { api } from "./api";

interface User {
  id: number;
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const saved = localStorage.getItem("mediguide_token");
    const savedUser = localStorage.getItem("mediguide_user");
    if (saved && savedUser) {
      setToken(saved);
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const handleAuth = (t: string, u: User) => {
    setToken(t);
    setUser(u);
    localStorage.setItem("mediguide_token", t);
    localStorage.setItem("mediguide_user", JSON.stringify(u));
  };

  const login = async (email: string, password: string) => {
    const { token: t, user: u } = await api.auth.login({ email, password });
    handleAuth(t, u);
  };

  const register = async (email: string, password: string, name: string) => {
    const { token: t, user: u } = await api.auth.register({ email, password, name });
    handleAuth(t, u);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("mediguide_token");
    localStorage.removeItem("mediguide_user");
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
