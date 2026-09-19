import React from 'react';
import {
  AlertCircle,
  Clock,
  HardDrive,
  Briefcase,
  CheckCircle2,
  ShieldAlert,
  ArrowUpRight,
  Sparkles,
  ExternalLink
} from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, PieChart, Pie, Cell } from 'recharts';
import { DashboardSummary } from '../types';
import { NavView } from '../components/Sidebar';

interface DashboardProps {
  data: DashboardSummary | null;
  loading: boolean;
  onNavigate: (view: NavView) => void;
}

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#ef4444', '#64748b'];

export const Dashboard: React.FC<DashboardProps> = ({ data, loading, onNavigate }) => {
  if (loading || !data) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3 text-slate-400">
          <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm">Synthesizing mailbox intelligence...</p>
        </div>
      </div>
    );
  }

  const { kpis, charts, recent_urgent, top_jobs } = data;

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Welcome & Prompt Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Email Intelligence Control Center</h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Agentic multi-signal analysis answering: <span className="text-indigo-400 font-medium">"What requires your attention right now?"</span>
          </p>
        </div>

        {kpis.pending_approvals > 0 && (
          <button
            onClick={() => onNavigate('approvals')}
            className="flex items-center gap-2.5 px-4 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-sm font-semibold transition shadow-lg shadow-rose-950/40 animate-pulse"
          >
            <ShieldAlert className="w-4 h-4 text-rose-400" />
            <span>{kpis.pending_approvals} Actions Pending Approval</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div
          onClick={() => onNavigate('inbox')}
          className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 hover:border-indigo-500/50 transition cursor-pointer group"
        >
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Unread Important</span>
            <AlertCircle className="w-4 h-4 text-amber-400 group-hover:scale-110 transition" />
          </div>
          <div className="text-3xl font-bold text-white">{kpis.unread_important}</div>
          <p className="text-xs text-slate-400 mt-1">High urgency/importance</p>
        </div>

        <div
          onClick={() => onNavigate('tasks')}
          className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 hover:border-indigo-500/50 transition cursor-pointer group"
        >
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Upcoming Deadlines</span>
            <Clock className="w-4 h-4 text-indigo-400 group-hover:scale-110 transition" />
          </div>
          <div className="text-3xl font-bold text-white">{kpis.upcoming_deadlines}</div>
          <p className="text-xs text-slate-400 mt-1">Tasks due within 72h</p>
        </div>

        <div
          onClick={() => onNavigate('storage')}
          className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 hover:border-indigo-500/50 transition cursor-pointer group"
        >
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Storage Waste</span>
            <HardDrive className="w-4 h-4 text-rose-400 group-hover:scale-110 transition" />
          </div>
          <div className="text-3xl font-bold text-white">{kpis.average_waste_score}<span className="text-base font-normal text-slate-500">/100</span></div>
          <p className="text-xs text-slate-400 mt-1">{kpis.recoverable_mb} MB recoverable</p>
        </div>

        <div
          onClick={() => onNavigate('jobs')}
          className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 hover:border-indigo-500/50 transition cursor-pointer group"
        >
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Job Opportunities</span>
            <Briefcase className="w-4 h-4 text-emerald-400 group-hover:scale-110 transition" />
          </div>
          <div className="text-3xl font-bold text-white">{kpis.job_opportunities}</div>
          <p className="text-xs text-emerald-400 font-medium mt-1">{kpis.high_match_jobs} High Match (≥70%)</p>
        </div>
      </div>

      {/* Analytics Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Categories Bar Chart */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/40 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-200">Email Category Distribution</h3>
            <span className="text-xs text-slate-400 font-mono">Real-time Extracted Classes</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.categories} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <XAxis dataKey="category" stroke="#64748b" fontSize={11} angle={-25} textAnchor="end" />
                <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#6366f1" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Storage Waste Donut */}
        <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-slate-200">Storage Waste Breakdown</h3>
              <span className="text-xs text-slate-400 font-mono">Algorithm Score</span>
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Emails categorized by computed Storage Waste Score
            </p>
          </div>
          <div className="h-44 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={charts.storage_waste}
                  dataKey="count"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={70}
                  paddingAngle={5}
                >
                  {charts.storage_waste.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-1.5 pt-2 border-t border-slate-800 text-xs">
            {charts.storage_waste.map((item, idx) => (
              <div key={item.name} className="flex items-center justify-between text-slate-300">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></span>
                  <span className="text-slate-400">{item.name}</span>
                </div>
                <span className="font-semibold">{item.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Urgent Emails & Job Opportunities Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Urgent Attention Emails */}
        <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400" />
              <h3 className="text-sm font-semibold text-slate-200">High-Priority Action Required</h3>
            </div>
            <button
              onClick={() => onNavigate('inbox')}
              className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium"
            >
              View all <ExternalLink className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-3">
            {recent_urgent.length === 0 ? (
              <p className="text-xs text-slate-500 py-6 text-center">No urgent emails requiring immediate action.</p>
            ) : (
              recent_urgent.map(item => (
                <div
                  key={item.id}
                  onClick={() => onNavigate('inbox')}
                  className="p-3.5 rounded-xl bg-slate-800/40 hover:bg-slate-800 border border-slate-700/40 transition cursor-pointer flex items-center justify-between gap-3"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="px-2 py-0.5 text-[10px] font-semibold rounded bg-rose-500/10 text-rose-300 border border-rose-500/20">
                        {item.category}
                      </span>
                      <span className="text-xs text-slate-400 truncate">{item.sender}</span>
                    </div>
                    <div className="text-xs font-semibold text-slate-200 truncate">{item.subject}</div>
                  </div>
                  <div className="text-right shrink-0">
                    <span className="text-[10px] font-mono text-amber-400 bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/20">
                      Urgency: {Math.round(item.urgency * 100)}%
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Top Job Matches */}
        <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-semibold text-slate-200">Career Intelligence Matches</h3>
            </div>
            <button
              onClick={() => onNavigate('jobs')}
              className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium"
            >
              View all jobs <ExternalLink className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-3">
            {top_jobs.length === 0 ? (
              <p className="text-xs text-slate-500 py-6 text-center">No job opportunities currently identified.</p>
            ) : (
              top_jobs.map(job => (
                <div
                  key={job.id}
                  onClick={() => onNavigate('jobs')}
                  className="p-3.5 rounded-xl bg-slate-800/40 hover:bg-slate-800 border border-slate-700/40 transition cursor-pointer flex items-center justify-between gap-3"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-bold text-white truncate">{job.role}</span>
                      <span className="text-xs text-indigo-400">@{job.company}</span>
                    </div>
                    <div className="flex items-center gap-2 text-[11px] text-slate-400">
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                        job.trust_level === 'LOW_RISK_SIGNALS'
                          ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20'
                          : 'bg-rose-500/10 text-rose-300 border border-rose-500/20'
                      }`}>
                        {job.trust_level === 'LOW_RISK_SIGNALS' ? 'Verified Sender' : 'Review Required'}
                      </span>
                      <span>Trust: {job.trust_score}%</span>
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <div className="text-sm font-bold text-emerald-400">{job.match_score}% Match</div>
                    <span className="text-[10px] text-slate-500 font-mono">Job Match Score</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
