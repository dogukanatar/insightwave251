"use client";
import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { login, register, logout, getDashboardData } from "@/services/api";
import { useRouter } from "next/navigation";

interface User {
  id: number;
  email: string;
  name: string;
  language: string;
  notification_method: string;
  active: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; message?: string }>;
  register: (name: string, email: string, password: string, topics: number[]) => Promise<{ success: boolean; message?: string }>;
  logout: () => Promise<{ success: boolean; message?: string }>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await getDashboardData();
        if (response.success && response.data) {
          setUser({
            id: response.data.id,
            email: response.data.email,
            name: response.data.name,
            language: response.data.language,
            notification_method: response.data.notification_method,
            active: response.data.active
          });
        }
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, []);

  const handleLogin = async (email: string, password: string) => {
    try {
      const response = await login(email, password);
      if (response.success && response.user) {
        setUser(response.user);
        router.push("/dashboard");
        return { success: true };
      }
      return { success: false, message: response.message || "Login failed" };
    } catch (error: any) {
      return { success: false, message: "Network error" };
    }
  };

  const handleRegister = async (name: string, email: string, password: string, topics: number[]) => {
    try {
      const response = await register(name, email, password, topics);
      if (response.success) {
        const loginResponse = await handleLogin(email, password);
        return loginResponse;
      }
      return { success: false, message: response.message || "Registration failed" };
    } catch (error: any) {
      return { success: false, message: "Network error" };
    }
  };

  const handleLogout = async () => {
    try {
      const response = await logout();
      if (response.success) {
        setUser(null);
        router.push("/login");
        return { success: true };
      }
      return { success: false, message: "Logout failed" };
    } catch (error) {
      return { success: false, message: "Network error" };
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login: handleLogin, register: handleRegister, logout: handleLogout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) throw new Error("useAuth must be used within an AuthProvider");
  return context;
};
