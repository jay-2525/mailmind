import React, { useState, useEffect } from 'react';
import {
  HardDrive,
  Trash2,
  Archive,
  Copy,
  AlertTriangle,
  CheckCircle2,
  Filter,
  ShieldCheck,
  ChevronRight
} from 'lucide-react';
import { StorageOverview, StorageItem } from '../types';
import { api } from '../services/api';

export const StorageIntelligence: React.FC = () => {
  const [overview, setOverview] = useState<StorageOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [filterMode, setFilterMode] = useState<'all' | 'high_waste' | 'duplicates' | 'large'>('all');
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const loadStorage = async () => {
    setLoading(true);
    try {
      const data = await api.getStorageOverview();
      setOverview(data);
    } catch (e) {
      console.error('Failed to load storage overview:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStorage();
  }, []);

  const toggleSelect = (id: string) => {
    const next = new Set(selectedIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelectedIds(next);
  };

  const selectAll = (items: StorageItem[]) => {
    if (selectedIds.size === items.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(items.map(i => i.email_id)));
    }
  };

  const handleStageCleanup = async (action: 'ARCHIVE' | 'DELETE') => {
    if (selectedIds.size === 0) return;
    try {
      const res = await api.stageStorageCleanup(Array.from(selectedIds), action);
      setActionMessage(res.message);
      setSelectedIds(new Set());
      setTimeout(() => setActionMessage(null), 5000);
      loadStorage();
    } catch (e: any) {
      alert(`Error staging cleanup: ${e.message}`);
    }
  };

  if (loading || !overview) {
    return <div className="p-8 text-center text-slate-400">Loading Storage Intelligence...</div>;
  }

  // Filter items based on filterMode
  let filteredItems = overview.items;
  if (filterMode === 'high_waste') {
    filteredItems = overview.items.filter(i => i.waste_score >= 60);
  } else if (filterMode === 'duplicates') {
    filteredItems = overview.items.filter(i => i.is_duplicate);
  } else if (filterMode === 'large') {
    filteredItems = overview.items.filter(i => i.size_bytes > 2 * 1024 * 1024);
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Smart Storage Cleanup</h2>
          <p className="text-sm text-slate-400 mt-1">
            Explainable Storage Waste Scoring and Semantic Redundancy Detection.
          </p>
        </div>

        {/* Batch Action Buttons */}
        {selectedIds.size > 0 && (
          <div className="flex items-center gap-3 animate-in fade-in slide-in-from-right-2">
            <span className="text-xs text-slate-300 font-medium">
              {selectedIds.size} selected
            </span>
            <button
              onClick={() => handleStageCleanup('ARCHIVE')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold transition"
            >
              <Archive className="w-3.5 h-3.5 text-indigo-400" />
              <span>Stage Archive</span>
            </button>
            <button
              onClick={() => handleStageCleanup('DELETE')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-semibold transition"
            >
              <Trash2 className="w-3.5 h-3.5 text-rose-400" />
              <span>Stage Delete</span>
            </button>
          </div>
        )}
      </div>

      {actionMessage && (
        <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-sm flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-indigo-400 shrink-0" />
          <span>{actionMessage}</span>
        </div>
      )}

      {/* Storage Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800">
          <div className="text-xs font-medium text-slate-400 uppercase">Total Mailbox Footprint</div>
          <div className="text-2xl font-bold text-white mt-1">
            {(overview.total_storage_bytes / (1024 * 1024)).toFixed(1)} MB
          </div>
          <div className="text-xs text-slate-500 mt-1">{overview.total_emails} total emails indexed</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800">
          <div className="text-xs font-medium text-slate-400 uppercase">Recoverable Storage</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">
            {(overview.recoverable_storage_bytes / (1024 * 1024)).toFixed(1)} MB
          </div>
          <div className="text-xs text-emerald-400/80 mt-1">Emails with waste score ≥ 60</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800">
          <div className="text-xs font-medium text-slate-400 uppercase">Average Waste Score</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">
            {overview.average_waste_score}<span className="text-sm font-normal text-slate-500">/100</span>
          </div>
          <div className="text-xs text-slate-500 mt-1">Weighted decision score</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800">
          <div className="text-xs font-medium text-slate-400 uppercase">Detected Redundancies</div>
          <div className="text-2xl font-bold text-rose-400 mt-1">
            {overview.duplicate_count}
          </div>
          <div className="text-xs text-slate-500 mt-1">Semantic duplicates identified</div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setFilterMode('all')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              filterMode === 'all' ? 'bg-indigo-600 text-white' : 'bg-slate-900 text-slate-400 hover:text-slate-200'
            }`}
          >
            All Items ({overview.items.length})
          </button>
          <button
            onClick={() => setFilterMode('high_waste')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              filterMode === 'high_waste' ? 'bg-indigo-600 text-white' : 'bg-slate-900 text-slate-400 hover:text-slate-200'
            }`}
          >
            High Waste (≥60)
          </button>
          <button
            onClick={() => setFilterMode('duplicates')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              filterMode === 'duplicates' ? 'bg-indigo-600 text-white' : 'bg-slate-900 text-slate-400 hover:text-slate-200'
            }`}
          >
            Duplicate Groups ({overview.duplicate_count})
          </button>
          <button
            onClick={() => setFilterMode('large')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              filterMode === 'large' ? 'bg-indigo-600 text-white' : 'bg-slate-900 text-slate-400 hover:text-slate-200'
            }`}
          >
            Large Payloads ({overview.large_attachments_count})
          </button>
        </div>

        <button
          onClick={() => selectAll(filteredItems)}
          className="text-xs text-indigo-400 hover:text-indigo-300 font-medium"
        >
          {selectedIds.size === filteredItems.length ? 'Deselect All' : 'Select All Filtered'}
        </button>
      </div>

      {/* Storage Items Table */}
      <div className="rounded-2xl bg-slate-900/40 border border-slate-800 overflow-hidden">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800 uppercase font-mono text-[10px]">
            <tr>
              <th className="py-3 px-4 w-10">
                <input
                  type="checkbox"
                  checked={selectedIds.size > 0 && selectedIds.size === filteredItems.length}
                  onChange={() => selectAll(filteredItems)}
                  className="rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-0"
                />
              </th>
              <th className="py-3 px-4">Subject & Sender</th>
              <th className="py-3 px-4">Category</th>
              <th className="py-3 px-4">Size</th>
              <th className="py-3 px-4">Waste Score</th>
              <th className="py-3 px-4">Why This Score?</th>
              <th className="py-3 px-4">Recommendation</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {filteredItems.map(item => {
              const isSelected = selectedIds.has(item.email_id);
              return (
                <tr
                  key={item.email_id}
                  className={`hover:bg-slate-800/30 transition ${isSelected ? 'bg-indigo-500/5' : ''}`}
                >
                  <td className="py-3 px-4">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggleSelect(item.email_id)}
                      className="rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-0"
                    />
                  </td>
                  <td className="py-3 px-4 max-w-xs">
                    <div className="font-semibold text-slate-200 truncate">{item.subject}</div>
                    <div className="text-[11px] text-slate-500 truncate">{item.sender}</div>
                  </td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-[10px]">
                      {item.category}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-400">
                    {(item.size_bytes / 1024).toFixed(1)} KB
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <div className="w-12 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                        <div
                          className={`h-full ${
                            item.waste_score >= 70 ? 'bg-rose-500' : item.waste_score >= 40 ? 'bg-amber-500' : 'bg-emerald-500'
                          }`}
                          style={{ width: `${item.waste_score}%` }}
                        ></div>
                      </div>
                      <span className="font-bold text-slate-200">{item.waste_score}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-[11px] text-slate-400">
                    {item.reasons.slice(0, 2).join(' · ') || 'Low penalty score'}
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`px-2 py-0.5 rounded font-semibold text-[10px] ${
                        item.recommended_action === 'DELETE'
                          ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                          : item.recommended_action === 'ARCHIVE'
                          ? 'bg-indigo-500/10 text-indigo-300 border border-indigo-500/20'
                          : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      }`}
                    >
                      {item.recommended_action}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
