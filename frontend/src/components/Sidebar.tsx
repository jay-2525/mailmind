import React from 'react';
import {
  LayoutDashboard,
  Inbox,
  HardDrive,
  CheckSquare,
  Briefcase,
  FileText,
  Calendar,
  ShieldAlert,
  BrainCircuit,
  GraduationCap,
  ScrollText,
  Settings
} from 'lucide-react';

export type NavView =
  | 'dashboard'
  | 'inbox'
  | 'storage'
  | 'tasks'
  | 'jobs'
  | 'resume'
  | 'calendar'
  | 'approvals'
  | 'rag'
  | 'academic'
  | 'audit'
  | 'settings';

interface SidebarProps {
  currentView: NavView;
  onSelectView: (view: NavView) => void;
  pendingApprovalsCount: number;
  urgentEmailsCount: number;
  openTasksCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentView,
  onSelectView,
  pendingApprovalsCount,
  urgentEmailsCount,
  openTasksCount
}) => {
  const navItems: Array<{
    id: NavView;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    badge?: number;
    badgeColor?: string;
    highlight?: boolean;
  }> = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'inbox', label: 'Inbox Intelligence', icon: Inbox, badge: urgentEmailsCount, badgeColor: 'bg-indigo-500/20 text-indigo-300' },
    { id: 'storage', label: 'Storage Cleanup', icon: HardDrive },
    { id: 'tasks', label: 'Tasks & Commitments', icon: CheckSquare, badge: openTasksCount, badgeColor: 'bg-emerald-500/20 text-emerald-300' },
    { id: 'jobs', label: 'Job Opportunities', icon: Briefcase },
    { id: 'resume', label: 'Resume Profile', icon: FileText },
    { id: 'calendar', label: 'Google Calendar', icon: Calendar },
    {
      id: 'approvals',
      label: 'Approval Center',
      icon: ShieldAlert,
      badge: pendingApprovalsCount,
      badgeColor: 'bg-rose-500/20 text-rose-300 border border-rose-500/30 font-bold',
      highlight: pendingApprovalsCount > 0
    },
    { id: 'rag', label: 'Historical RAG', icon: BrainCircuit },
    {
      id: 'academic',
      label: 'Academic Viva Mode',
      icon: GraduationCap,
      highlight: true
    },
    { id: 'audit', label: 'Audit Logs', icon: ScrollText },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-900/40 flex flex-col justify-between shrink-0 h-[calc(100vh-4rem)] sticky top-16">
      <div className="p-4 space-y-1 overflow-y-auto">
        <div className="px-3 py-2 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
          Core Navigation
        </div>

        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectView(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20'
                  : item.highlight && item.id === 'academic'
                  ? 'text-amber-300 hover:bg-amber-500/10 border border-amber-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : item.id === 'academic' ? 'text-amber-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && item.badge > 0 && (
                <span className={`px-2 py-0.5 text-xs rounded-full ${item.badgeColor || 'bg-slate-800 text-slate-300'}`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Safety Banner at bottom of sidebar */}
      <div className="p-4 border-t border-slate-800/60">
        <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/50 text-xs text-slate-400">
          <div className="flex items-center gap-1.5 font-semibold text-slate-300 mb-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            Policy Guard: STRICT
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Email content treated as untrusted input. Destructive actions require user approval.
          </p>
        </div>
      </div>
    </aside>
  );
};
