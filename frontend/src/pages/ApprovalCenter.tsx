import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  CheckCircle2,
  XCircle,
  Edit3,
  AlertTriangle,
  HardDrive,
  FileText,
  Calendar,
  Send
} from 'lucide-react';
import { ApprovalItem } from '../types';
import { api } from '../services/api';

export const ApprovalCenter: React.FC = () => {
  const [approvals, setApprovals] = useState<ApprovalItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<'PENDING' | 'APPROVED' | 'REJECTED'>('PENDING');
  const [actioningId, setActioningId] = useState<string | null>(null);
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);

  const loadApprovals = async () => {
    setLoading(true);
    try {
      const data = await api.getApprovals(statusFilter);
      setApprovals(data);
    } catch (e) {
      console.error('Failed to load approvals:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApprovals();
  }, [statusFilter]);

  const handleAction = async (approvalId: string, action: 'APPROVE' | 'REJECT') => {
    setActioningId(approvalId);
    try {
      const res = await api.actOnApproval(approvalId, action);
      setFeedbackMessage(res.message);
      setTimeout(() => setFeedbackMessage(null), 4000);
      loadApprovals();
    } catch (e: any) {
      alert(`Action error: ${e.message}`);
    } finally {
      setActioningId(null);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Human-in-the-Loop Approval Center</h2>
          <p className="text-sm text-slate-400 mt-1">
            Mandatory authorization gate for destructive, external, or high-risk agent recommendations.
          </p>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-2 bg-slate-900/60 p-1 rounded-xl border border-slate-800">
          {(['PENDING', 'APPROVED', 'REJECTED'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setStatusFilter(tab)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                statusFilter === tab
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {feedbackMessage && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-sm flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{feedbackMessage}</span>
        </div>
      )}

      {/* Approvals Queue */}
      {loading ? (
        <div className="p-12 text-center text-slate-400">Loading approval queue...</div>
      ) : approvals.length === 0 ? (
        <div className="p-16 text-center rounded-2xl bg-slate-900/30 border border-slate-800 text-slate-500 space-y-2">
          <CheckCircle2 className="w-8 h-8 text-emerald-400/60 mx-auto" />
          <p className="text-sm">No actions currently in {statusFilter} status.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {approvals.map(appr => {
            const isPending = appr.status === 'PENDING';
            const isHighRisk = appr.risk_level === 'HIGH';

            return (
              <div
                key={appr.id}
                className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4 hover:border-slate-700/80 transition"
              >
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                  <div className="space-y-1.5 flex-1">
                    <div className="flex items-center gap-2">
                      <span className={`px-2.5 py-0.5 rounded-md text-xs font-bold uppercase tracking-wider ${
                        appr.action_type === 'DELETE' ? 'bg-rose-500/10 text-rose-300 border border-rose-500/20' :
                        appr.action_type === 'ARCHIVE' ? 'bg-indigo-500/10 text-indigo-300 border border-indigo-500/20' :
                        'bg-amber-500/10 text-amber-300 border border-amber-500/20'
                      }`}>
                        Action: {appr.action_type}
                      </span>

                      <span className={`px-2 py-0.5 rounded-md text-[11px] font-bold ${
                        isHighRisk ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'bg-amber-500/20 text-amber-300'
                      }`}>
                        Risk: {appr.risk_level}
                      </span>

                      <span className="text-xs text-slate-500 font-mono">
                        {new Date(appr.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>

                    <h3 className="text-sm font-bold text-white tracking-tight">
                      Target: {appr.target_resource}
                    </h3>
                  </div>

                  {/* Status Badge */}
                  <span className={`px-3 py-1 rounded-full text-xs font-bold shrink-0 ${
                    appr.status === 'PENDING' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30 animate-pulse' :
                    appr.status === 'APPROVED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
                    'bg-slate-800 text-slate-400'
                  }`}>
                    {appr.status}
                  </span>
                </div>

                {/* AI Reasoning & Consequences Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1">
                    <span className="font-semibold text-slate-300">AI Recommendation Rationale:</span>
                    <p className="text-slate-400 leading-relaxed">{appr.reason}</p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1">
                    <span className="font-semibold text-slate-300">Consequences & Side Effects:</span>
                    <p className="text-slate-400 leading-relaxed">{appr.consequences || 'Will modify mailbox state according to user policy.'}</p>
                  </div>
                </div>

                {/* Evidence Payload */}
                {appr.evidence && Object.keys(appr.evidence).length > 0 && (
                  <div className="p-3 rounded-xl bg-slate-950/40 border border-slate-800 text-[11px] font-mono text-slate-400">
                    <span className="text-slate-500">Evidence Context:</span> {JSON.stringify(appr.evidence)}
                  </div>
                )}

                {/* Action Buttons if Pending */}
                {isPending && (
                  <div className="pt-3 border-t border-slate-800 flex items-center justify-end gap-3">
                    <button
                      onClick={() => handleAction(appr.id, 'REJECT')}
                      disabled={actioningId === appr.id}
                      className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition disabled:opacity-50"
                    >
                      <XCircle className="w-3.5 h-3.5 text-slate-400" />
                      <span>Reject Action</span>
                    </button>

                    <button
                      onClick={() => handleAction(appr.id, 'APPROVE')}
                      disabled={actioningId === appr.id}
                      className={`flex items-center gap-1.5 px-4 py-1.5 rounded-xl text-white text-xs font-semibold shadow-lg transition disabled:opacity-50 ${
                        isHighRisk
                          ? 'bg-rose-600 hover:bg-rose-500 shadow-rose-600/20'
                          : 'bg-indigo-600 hover:bg-indigo-500 shadow-indigo-600/20'
                      }`}
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>{isHighRisk ? 'Authorize Destructive Action' : 'Authorize Action'}</span>
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
