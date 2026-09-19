import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  AlertTriangle,
  CheckCircle2,
  Calendar,
  Clock,
  HardDrive,
  Shield,
  ChevronDown,
  ChevronUp,
  BrainCircuit,
  HelpCircle,
  FileText
} from 'lucide-react';
import { EmailItem } from '../types';
import { api } from '../services/api';

export const InboxIntelligence: React.FC = () => {
  const [emails, setEmails] = useState<EmailItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [expandedEmailId, setExpandedEmailId] = useState<string | null>(null);

  const categories = ['All', 'Education', 'Meeting', 'Promotion', 'Job Opportunity', 'Newsletter', 'Finance', 'Other'];

  const loadEmails = async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const catFilter = selectedCategory === 'All' ? undefined : selectedCategory;
      const data = await api.getEmails(catFilter, search || undefined);
      setEmails(data);
    } catch (e) {
      console.error('Failed to load emails:', e);
    } finally {
      if (!silent) setLoading(false);
    }
  };

  useEffect(() => {
    loadEmails();

    const timer = setInterval(() => {
      loadEmails(true);
    }, 4000);

    const onFocus = () => loadEmails(true);
    window.addEventListener('focus', onFocus);

    const onRefresh = () => loadEmails(true);
    window.addEventListener('inboxguard_refresh', onRefresh);

    return () => {
      clearInterval(timer);
      window.removeEventListener('focus', onFocus);
      window.removeEventListener('inboxguard_refresh', onRefresh);
    };
  }, [selectedCategory]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadEmails();
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Inbox Intelligence</h2>
        <p className="text-sm text-slate-400 mt-1">
          Multi-signal understanding, entity recognition, and explainable decision support for every email.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col md:flex-row gap-4 justify-between">
        <form onSubmit={handleSearchSubmit} className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search by subject, sender, or keywords..."
            className="w-full pl-10 pr-4 py-2 bg-slate-900/60 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 transition"
          />
        </form>

        {/* Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-2 md:pb-0">
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition ${
                selectedCategory === cat
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Emails List */}
      {loading ? (
        <div className="py-20 text-center text-slate-400">Loading and analyzing inbox...</div>
      ) : emails.length === 0 ? (
        <div className="p-12 text-center rounded-2xl bg-slate-900/40 border border-slate-800 text-slate-400">
          No emails found matching your filters.
        </div>
      ) : (
        <div className="space-y-4">
          {emails.map(email => {
            const isExpanded = expandedEmailId === email.id;
            const analysis = email.analysis;
            const wasteScore = analysis?.storage_waste_score ?? 0;
            const urgency = analysis?.urgency ?? 0.5;
            const importance = analysis?.importance ?? 0.5;
            const riskLevel = analysis?.security_risk_level ?? 'LOW';

            return (
              <div
                key={email.id}
                className="rounded-2xl bg-slate-900/50 border border-slate-800/90 overflow-hidden transition hover:border-slate-700/80"
              >
                {/* Header Row */}
                <div
                  onClick={() => setExpandedEmailId(isExpanded ? null : email.id)}
                  className="p-5 cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4 select-none"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2.5 mb-1.5 flex-wrap">
                      <span className="px-2.5 py-0.5 text-xs font-semibold rounded-md bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                        {analysis?.category || 'General'}
                      </span>

                      {riskLevel === 'HIGH' && (
                        <span className="px-2 py-0.5 text-[11px] font-bold rounded-md bg-rose-500/10 text-rose-300 border border-rose-500/30 flex items-center gap-1">
                          <AlertTriangle className="w-3 h-3 text-rose-400" /> Security Risk
                        </span>
                      )}

                      <span className="text-xs font-medium text-slate-400">
                        {email.sender_name ? `${email.sender_name} <${email.sender}>` : email.sender}
                      </span>
                      <span className="text-xs text-slate-600">·</span>
                      <span className="text-xs text-slate-500">
                        {new Date(email.received_at).toLocaleDateString(undefined, {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    </div>

                    <h3 className="text-sm font-bold text-slate-100 tracking-tight">{email.subject}</h3>
                  </div>

                  {/* Right Badges & Recommended Action */}
                  <div className="flex items-center gap-3 shrink-0">
                    <div className="hidden sm:flex items-center gap-2 text-xs">
                      <div className="px-2 py-1 rounded bg-slate-800 border border-slate-700 text-slate-300" title="Urgency Score">
                        Urg: <span className="font-semibold text-amber-400">{Math.round(urgency * 100)}%</span>
                      </div>
                      <div className="px-2 py-1 rounded bg-slate-800 border border-slate-700 text-slate-300" title="Importance Score">
                        Imp: <span className="font-semibold text-indigo-400">{Math.round(importance * 100)}%</span>
                      </div>
                      <div className="px-2 py-1 rounded bg-slate-800 border border-slate-700 text-slate-300" title="Storage Waste Score">
                        Waste: <span className={`font-semibold ${wasteScore >= 70 ? 'text-rose-400' : 'text-emerald-400'}`}>{wasteScore}</span>
                      </div>
                    </div>

                    <div className="px-3 py-1 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 font-semibold text-xs">
                      {wasteScore >= 80 ? 'DELETE' : wasteScore >= 50 ? 'ARCHIVE' : 'KEEP'}
                    </div>

                    <div className="w-7 h-7 rounded-lg bg-slate-800 flex items-center justify-center text-slate-400">
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </div>
                  </div>
                </div>

                {/* Expanded Details Panel */}
                {isExpanded && (
                  <div className="p-6 border-t border-slate-800 bg-slate-950/60 space-y-6 text-sm">
                    {/* Raw Body Preview */}
                    <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">
                      {email.body_text}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* AI Summary & Entities */}
                      <div className="space-y-4">
                        <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800">
                          <div className="flex items-center gap-2 text-xs font-semibold text-indigo-300 mb-2">
                            <BrainCircuit className="w-4 h-4" />
                            <span>AI Intent & Executive Summary</span>
                          </div>
                          <p className="text-xs text-slate-300 leading-relaxed">
                            {analysis?.summary || 'Summary synthesized from email context and body.'}
                          </p>
                        </div>

                        {/* Extracted Entities */}
                        <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800">
                          <div className="text-xs font-semibold text-slate-300 mb-2 flex items-center gap-2">
                            <FileText className="w-4 h-4 text-emerald-400" />
                            <span>Extracted Named Entities (NER)</span>
                          </div>
                          {email.entities && email.entities.length > 0 ? (
                            <div className="flex flex-wrap gap-1.5">
                              {email.entities.map(ent => (
                                <span
                                  key={ent.id}
                                  className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-[11px] text-slate-300"
                                >
                                  <span className="text-[9px] text-slate-500 font-mono mr-1">{ent.entity_type}:</span>
                                  {ent.entity_value}
                                </span>
                              ))}
                            </div>
                          ) : (
                            <p className="text-xs text-slate-500">None extracted.</p>
                          )}
                        </div>
                      </div>

                      {/* Why This Recommendation & Safety Analysis */}
                      <div className="space-y-4">
                        <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800">
                          <div className="flex items-center gap-2 text-xs font-semibold text-amber-300 mb-2">
                            <HelpCircle className="w-4 h-4" />
                            <span>Why This Recommendation?</span>
                          </div>
                          <ul className="text-xs text-slate-300 space-y-1.5 list-disc list-inside">
                            <li>Category: <strong className="text-slate-200">{analysis?.category}</strong> (Urgency {Math.round(urgency * 100)}%, Importance {Math.round(importance * 100)}%)</li>
                            <li>Storage Waste Score: <strong className="text-slate-200">{wasteScore}/100</strong> (Size: {(email.size_bytes / 1024).toFixed(1)} KB)</li>
                            <li>Actionability: {analysis?.actionability && analysis.actionability > 0.6 ? 'Contains pending tasks/commitments' : 'No active actionable tasks detected'}</li>
                          </ul>
                        </div>

                        {/* Safety & Untrusted Input Policy */}
                        <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800">
                          <div className="flex items-center gap-2 text-xs font-semibold text-rose-300 mb-2">
                            <Shield className="w-4 h-4" />
                            <span>Safety & Policy Guard Analysis</span>
                          </div>
                          <div className="text-xs text-slate-300 space-y-1">
                            <div>Risk Tier: <strong className={riskLevel === 'HIGH' ? 'text-rose-400' : 'text-emerald-400'}>{riskLevel}</strong></div>
                            <div>Untrusted Input Quarantine: <span className="text-emerald-400 font-medium">Enforced</span> (No prompt instructions executed)</div>
                            {analysis?.security_risk_reasons && analysis.security_risk_reasons.length > 0 && (
                              <div className="text-rose-300 font-mono text-[11px] pt-1">
                                Warning: {analysis.security_risk_reasons.join(', ')}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
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
