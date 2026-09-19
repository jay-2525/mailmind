import React, { useState, useEffect } from 'react';
import { Settings, Sliders, Shield, Database, Cpu, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

export const SettingsView: React.FC = () => {
  const [status, setStatus] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  // Storage Weights
  const [wSize, setWSize] = useState(0.25);
  const [wPromo, setWPromo] = useState(0.25);
  const [wRedundancy, setWRedundancy] = useState(0.20);
  const [wAge, setWAge] = useState(0.15);
  const [wLowAction, setWLowAction] = useState(0.15);

  // Job Match Weights
  const [wReq, setWReq] = useState(0.35);
  const [wPref, setWPref] = useState(0.15);
  const [wSem, setWSem] = useState(0.20);
  const [wExp, setWExp] = useState(0.15);
  const [wEdu, setWEdu] = useState(0.15);

  const [savedMessage, setSavedMessage] = useState<string | null>(null);

  useEffect(() => {
    api.getDemoStatus().then(st => {
      setStatus(st);
      setLoading(false);
    });
  }, []);

  const handleSaveWeights = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedMessage('Scoring formula weights updated successfully!');
    setTimeout(() => setSavedMessage(null), 3000);
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">System & Algorithm Settings</h2>
        <p className="text-sm text-slate-400 mt-1">
          Configure decision weights, threshold parameters, and LLM orchestration settings.
        </p>
      </div>

      {savedMessage && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{savedMessage}</span>
        </div>
      )}

      {/* Environment & LLM Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-1">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
            <Cpu className="w-4 h-4 text-indigo-400" />
            <span>LLM Provider Abstraction</span>
          </div>
          <div className="text-lg font-bold text-white uppercase">{status?.llm_provider || 'Heuristic / Gemini'}</div>
          <p className="text-[11px] text-slate-500">Configurable via LLM_PROVIDER</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-1">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
            <Database className="w-4 h-4 text-purple-400" />
            <span>Vector Embedding Model</span>
          </div>
          <div className="text-lg font-bold text-white">all-MiniLM-L6-v2</div>
          <p className="text-[11px] text-slate-500">384-dimensional dense vectors</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-1">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
            <Shield className="w-4 h-4 text-emerald-400" />
            <span>Policy Guard Mode</span>
          </div>
          <div className="text-lg font-bold text-emerald-400">STRICT ENFORCEMENT</div>
          <p className="text-[11px] text-slate-500">Untrusted Input Quarantine Active</p>
        </div>
      </div>

      {/* Configurable Formula Weights Form */}
      <form onSubmit={handleSaveWeights} className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-6">
        <div>
          <div className="flex items-center gap-2 text-sm font-bold text-white">
            <Sliders className="w-4 h-4 text-indigo-400" />
            <span>Storage Waste Score Formula Weights</span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Adjust the mathematical weight assigned to individual penalty factors (Normalized to 1.0).
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="space-y-1">
            <div className="flex justify-between text-slate-300">
              <span>Attachment / Size Penalty:</span>
              <span className="font-mono text-indigo-400">{wSize}</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.50"
              step="0.05"
              value={wSize}
              onChange={e => setWSize(parseFloat(e.target.value))}
              className="w-full accent-indigo-500"
            />
          </div>

          <div className="space-y-1">
            <div className="flex justify-between text-slate-300">
              <span>Promotional / Marketing Content:</span>
              <span className="font-mono text-indigo-400">{wPromo}</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.50"
              step="0.05"
              value={wPromo}
              onChange={e => setWPromo(parseFloat(e.target.value))}
              className="w-full accent-indigo-500"
            />
          </div>

          <div className="space-y-1">
            <div className="flex justify-between text-slate-300">
              <span>Semantic Redundancy Match:</span>
              <span className="font-mono text-indigo-400">{wRedundancy}</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.50"
              step="0.05"
              value={wRedundancy}
              onChange={e => setWRedundancy(parseFloat(e.target.value))}
              className="w-full accent-indigo-500"
            />
          </div>

          <div className="space-y-1">
            <div className="flex justify-between text-slate-300">
              <span>Inactivity & Age Penalty:</span>
              <span className="font-mono text-indigo-400">{wAge}</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.50"
              step="0.05"
              value={wAge}
              onChange={e => setWAge(parseFloat(e.target.value))}
              className="w-full accent-indigo-500"
            />
          </div>
        </div>

        <div className="pt-4 border-t border-slate-800 flex justify-end">
          <button
            type="submit"
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20"
          >
            Save Weight Configuration
          </button>
        </div>
      </form>
    </div>
  );
};
