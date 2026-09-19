import React, { useState } from 'react';
import { Shield, RefreshCw, Sparkles, User, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

interface NavbarProps {
  onDataRefresh?: () => void;
  pendingApprovalsCount?: number;
}

export const Navbar: React.FC<NavbarProps> = ({ onDataRefresh, pendingApprovalsCount = 0 }) => {
  const [syncing, setSyncing] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleSync = async () => {
    setSyncing(true);
    try {
      const res = await api.syncEmails();
      setMessage(res.message);
      setTimeout(() => setMessage(null), 4000);
      if (onDataRefresh) onDataRefresh();
    } catch (e: any) {
      setMessage(`Sync failed: ${e.message}`);
      setTimeout(() => setMessage(null), 4000);
    } finally {
      setSyncing(false);
    }
  };

  const handleResetDemo = async () => {
    if (!window.confirm('Reset all demo data back to clean initial state?')) return;
    setResetting(true);
    try {
      const res = await api.resetDemoData();
      setMessage(res.message);
      setTimeout(() => setMessage(null), 4000);
      if (onDataRefresh) onDataRefresh();
    } catch (e: any) {
      setMessage(`Reset failed: ${e.message}`);
      setTimeout(() => setMessage(null), 4000);
    } finally {
      setResetting(false);
    }
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <Shield className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-white tracking-tight">InboxGuard</h1>
            <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Demo Mode Active
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-mono">
            MailMind · Agentic AI for Smart Email & Career Intelligence
          </p>
        </div>
      </div>

      {/* Center status message if any */}
      {message && (
        <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs animate-in fade-in slide-in-from-top-1 duration-200">
          <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
          <span>{message}</span>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-3">
        <button
          onClick={handleSync}
          disabled={syncing}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition disabled:opacity-50"
          title="Run LangGraph Agent to analyze pending mailbox items"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin text-indigo-400' : 'text-slate-400'}`} />
          <span>{syncing ? 'Analyzing Mailbox...' : 'Sync Mailbox'}</span>
        </button>

        <button
          onClick={handleResetDemo}
          disabled={resetting}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 transition disabled:opacity-50"
          title="Reset seeded emails, resume, and approvals"
        >
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <span>{resetting ? 'Resetting...' : 'Reset Demo Data'}</span>
        </button>

        <div className="h-5 w-px bg-slate-800 mx-1"></div>

        {/* User Pill */}
        <div className="flex items-center gap-2.5 pl-1">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-xs font-bold text-white shadow">
            AM
          </div>
          <div className="hidden sm:block text-left">
            <div className="text-xs font-semibold text-slate-200">Alex Morgan</div>
            <div className="text-[10px] text-slate-400 font-mono">alex.morgan@university.edu</div>
          </div>
        </div>
      </div>
    </header>
  );
};
