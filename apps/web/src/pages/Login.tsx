import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Sparkles, ArrowRight, ShieldCheck, Lock, Mail, AlertCircle } from 'lucide-react';
import { useAuthStore } from '../stores/useAuthStore';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login, error, isLoading } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;
    const success = await login(email, password);
    if (success) {
      navigate('/');
    }
  };

  const handleDemoLogin = async () => {
    setEmail('operator@novax.local');
    setPassword('SuperSecretPassword123!');
    const success = await login('operator@novax.local', 'SuperSecretPassword123!');
    if (success) {
      navigate('/');
    }
  };

  return (
    <div className="min-h-screen w-screen bg-nova-950 flex items-center justify-center p-6 relative overflow-hidden font-sans">
      {/* Background ambient glow */}
      <div className="absolute top-1/4 -left-32 w-96 h-96 bg-nova-accent/15 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-nova-cyan/15 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md relative z-10 space-y-6">
        {/* Brand header */}
        <div className="text-center space-y-2">
          <div className="inline-flex h-12 w-12 rounded-2xl bg-gradient-to-tr from-nova-accent to-nova-cyan items-center justify-center shadow-glow-md">
            <Sparkles className="h-6 w-6 text-white" />
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-wider">NOVA X</h1>
          <p className="text-xs text-slate-400 font-medium">Personal Intelligence Operating System</p>
        </div>

        {/* Auth Card */}
        <div className="glass-panel-elevated p-8 rounded-2xl shadow-2xl space-y-6">
          <div className="space-y-1">
            <h2 className="text-lg font-bold text-white">Sign In</h2>
            <p className="text-xs text-slate-400">Enter your credentials to access your intelligence workspace</p>
          </div>

          {error && (
            <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-2.5 text-xs text-rose-400">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-3 h-4 w-4 text-slate-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="operator@novax.local"
                  required
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-nova-900 border border-nova-800 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-nova-accent transition-colors"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-slate-300">Password</label>
              </div>
              <div className="relative">
                <Lock className="absolute left-3.5 top-3 h-4 w-4 text-slate-500" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-nova-900 border border-nova-800 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-nova-accent transition-colors"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-nova-accent to-blue-600 hover:from-blue-600 hover:to-nova-accent text-white font-semibold text-xs shadow-glow-sm hover:shadow-glow-md transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <span>{isLoading ? 'Authenticating...' : 'Sign In'}</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </form>

          <div className="relative flex items-center justify-center">
            <div className="border-t border-nova-800 w-full" />
            <span className="bg-nova-900 px-3 text-[11px] text-slate-500 absolute">or</span>
          </div>

          <button
            type="button"
            onClick={handleDemoLogin}
            className="w-full py-2.5 rounded-xl bg-nova-850 hover:bg-nova-800 border border-nova-750 text-slate-300 font-medium text-xs transition-colors"
          >
            Sign in as Demo Operator
          </button>

          <div className="text-center text-xs text-slate-400">
            Don't have an account?{' '}
            <Link to="/register" className="text-nova-accent hover:underline font-semibold">
              Create Account
            </Link>
          </div>
        </div>

        {/* Security Footer Notice */}
        <div className="flex items-center justify-center gap-2 text-[11px] text-slate-500">
          <ShieldCheck className="h-4 w-4 text-nova-emerald" />
          <span>Zero-Trust Policy Engine & Authenticated Session</span>
        </div>
      </div>
    </div>
  );
};
