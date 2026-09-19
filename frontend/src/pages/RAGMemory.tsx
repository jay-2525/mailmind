import React, { useState } from 'react';
import {
  BrainCircuit,
  Search,
  Sparkles,
  HelpCircle,
  FileText,
  Clock,
  ArrowRight
} from 'lucide-react';
import { api } from '../services/api';

export const RAGMemory: React.FC = () => {
  const [query, setQuery] = useState('distributed systems project submission');
  const [results, setResults] = useState<any[]>([]);
  const [summary, setSummary] = useState<string>('');
  const [searching, setSearching] = useState(false);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;
    setSearching(true);
    try {
      const res = await api.searchRAG(query);
      setResults(res.results || []);
      setSummary(res.context_summary || '');
    } catch (e: any) {
      alert(`RAG Search Error: ${e.message}`);
    } finally {
      setSearching(false);
    }
  };

  const sampleQueries = [
    'distributed systems project submission deadline',
    'software engineer internship Google',
    'sprint review meeting demo',
    'AI research paper draft Section 4 evaluation'
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Historical RAG Memory Explorer</h2>
        <p className="text-sm text-slate-400 mt-1">
          Demonstrates Hybrid Vector & Keyword Retrieval with explicit explainability for B.Tech project evaluation.
        </p>
      </div>

      {/* Query Bar */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Search historical mailbox context..."
              className="w-full pl-10 pr-4 py-2.5 bg-slate-950/80 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>
          <button
            type="submit"
            disabled={searching}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20 transition disabled:opacity-50 shrink-0"
          >
            <BrainCircuit className="w-4 h-4" />
            <span>{searching ? 'Querying RAG...' : 'Search Context'}</span>
          </button>
        </form>

        {/* Suggested Queries */}
        <div className="flex items-center gap-2 flex-wrap text-xs text-slate-400">
          <span className="text-slate-500 font-medium">Try query:</span>
          {sampleQueries.map(sq => (
            <button
              key={sq}
              onClick={() => { setQuery(sq); }}
              className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700/60 text-[11px] transition"
            >
              "{sq}"
            </button>
          ))}
        </div>
      </div>

      {summary && (
        <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-indigo-400 shrink-0" />
          <span>{summary}</span>
        </div>
      )}

      {/* Results List */}
      <div className="space-y-4">
        {results.length === 0 ? (
          <div className="p-12 text-center rounded-2xl bg-slate-900/30 border border-slate-800 text-slate-500">
            Enter a query above to execute hybrid vector & keyword retrieval.
          </div>
        ) : (
          results.map((item, idx) => (
            <div
              key={item.email_id}
              className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-4 hover:border-slate-700 transition"
            >
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 uppercase">
                      Rank #{idx + 1} · {item.retrieval_method}
                    </span>
                    <span className="text-xs text-slate-400">{item.sender}</span>
                    <span className="text-xs text-slate-600">·</span>
                    <span className="text-xs text-slate-500">{new Date(item.received_at).toLocaleDateString()}</span>
                  </div>
                  <h3 className="text-base font-bold text-white tracking-tight">{item.subject}</h3>
                </div>

                <div className="text-right shrink-0">
                  <div className="text-lg font-bold text-indigo-400 font-mono">
                    {(item.similarity_score * 100).toFixed(1)}%
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">Hybrid Score</span>
                </div>
              </div>

              {/* Snippet */}
              <p className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed">
                {item.snippet}
              </p>

              {/* Explainability Highlight Box */}
              <div className="p-3.5 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs flex items-start gap-2.5">
                <HelpCircle className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="text-purple-200">Why was this historical email retrieved?</strong>
                  <p className="text-[11px] text-purple-300/90 mt-0.5">{item.reason_for_retrieval}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
