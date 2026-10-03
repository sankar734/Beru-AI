import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './stores/useAuthStore';
import { AppLayout } from './components/layout/AppLayout';

import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { Chat } from './pages/Chat';
import { Search } from './pages/Search';
import { Research } from './pages/Research';
import { Studio } from './pages/Studio';
import { Code } from './pages/Code';
import { Learn } from './pages/Learn';
import { Projects } from './pages/Projects';
import { Files } from './pages/Files';
import { Experts } from './pages/Experts';
import { Agents } from './pages/Agents';
import { Workflows } from './pages/Workflows';
import { Tasks } from './pages/Tasks';
import { Goals } from './pages/Goals';
import { Desktop } from './pages/Desktop';
import { Developer } from './pages/Developer';
import { Settings } from './pages/Settings';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="h-screen w-screen bg-nova-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 rounded-full border-2 border-nova-accent border-t-transparent animate-spin" />
          <span className="text-xs font-mono text-slate-400">Initializing NOVA X Core...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

export default function App() {
  const { checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <Routes>
      {/* Public Authentication Routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected Application Routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="chat" element={<Chat />} />
        <Route path="chat/:id" element={<Chat />} />
        <Route path="search" element={<Search />} />
        <Route path="research" element={<Research />} />
        <Route path="studio" element={<Studio />} />
        <Route path="code" element={<Code />} />
        <Route path="learn" element={<Learn />} />
        <Route path="projects" element={<Projects />} />
        <Route path="files" element={<Files />} />
        <Route path="experts" element={<Experts />} />
        <Route path="agents" element={<Agents />} />
        <Route path="workflows" element={<Workflows />} />
        <Route path="tasks" element={<Tasks />} />
        <Route path="goals" element={<Goals />} />
        <Route path="desktop" element={<Desktop />} />
        <Route path="desktop/developer" element={<Developer />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
