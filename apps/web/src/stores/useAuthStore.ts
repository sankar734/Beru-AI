import { create } from 'zustand';

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  created_at: string;
  preferences?: Record<string, unknown>;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  setAuth: (user: User, token: string) => void;
  clearAuth: () => void;
  checkAuth: () => Promise<void>;
  login: (email: string, password: string) => Promise<boolean>;
  register: (name: string, email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem('nova_token'),
  isAuthenticated: !!localStorage.getItem('nova_token'),
  isLoading: true,
  error: null,

  setAuth: (user, token) => {
    localStorage.setItem('nova_token', token);
    set({ user, token, isAuthenticated: true, error: null, isLoading: false });
  },

  clearAuth: () => {
    localStorage.removeItem('nova_token');
    set({ user: null, token: null, isAuthenticated: false, error: null, isLoading: false });
  },

  checkAuth: async () => {
    const token = localStorage.getItem('nova_token');
    if (!token) {
      set({ user: null, token: null, isAuthenticated: false, isLoading: false });
      return;
    }

    try {
      const res = await fetch('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const user = await res.json();
        set({ user, token, isAuthenticated: true, isLoading: false });
      } else {
        localStorage.removeItem('nova_token');
        set({ user: null, token: null, isAuthenticated: false, isLoading: false });
      }
    } catch {
      // In offline/demo mode, if token exists, create session state
      set({
        user: {
          id: 'demo-user',
          email: 'operator@novax.local',
          name: 'Nova Operator',
          role: 'admin',
          created_at: new Date().toISOString(),
        },
        isAuthenticated: true,
        isLoading: false,
      });
    }
  },

  login: async (email, password) => {
    set({ error: null, isLoading: true });
    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (!res.ok) {
        set({ error: data.detail || 'Login failed', isLoading: false });
        return false;
      }
      get().setAuth(data.user, data.access_token);
      return true;
    } catch {
      set({ error: 'Connection error during login', isLoading: false });
      return false;
    }
  },

  register: async (name, email, password) => {
    set({ error: null, isLoading: true });
    try {
      const res = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password }),
      });
      const data = await res.json();
      if (!res.ok) {
        set({ error: data.detail || 'Registration failed', isLoading: false });
        return false;
      }
      get().setAuth(data.user, data.access_token);
      return true;
    } catch {
      set({ error: 'Connection error during registration', isLoading: false });
      return false;
    }
  },

  logout: async () => {
    const token = get().token;
    if (token) {
      try {
        await fetch('/api/v1/auth/logout', {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        });
      } catch {
        // Ignore network errors on logout
      }
    }
    get().clearAuth();
  },
}));
