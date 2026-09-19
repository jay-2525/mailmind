import React, { useState, useEffect } from 'react';
import {
  Briefcase,
  ShieldCheck,
  AlertTriangle,
  Sparkles,
  ExternalLink,
  CheckCircle2,
  XCircle,
  Copy,
  FileText,
  MapPin,
  DollarSign,
  Send
} from 'lucide-react';
import { JobItem, JobMatch } from '../types';
import { api } from '../services/api';

export const JobIntelligence: React.FC = () => {
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState<JobItem | null>(null);
  const [applicationPack, setApplicationPack] = useState<any | null>(null);
  const [preparing, setPreparing] = useState(false);
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const loadJobs = async () => {
    setLoading(true);
    try {
      const data = await api.getJobs();
      setJobs(data);
    } catch (e) {
      console.error('Failed to load jobs:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, []);

  const handlePrepareApplication = async (job: JobItem) => {
    setSelectedJob(job);
    setPreparing(true);
    try {
      const res = await api.prepareJobApplication(job.id);
      setApplicationPack(res);
    } catch (e: any) {
      alert(`Could not prepare application: ${e.message}`);
    } finally {
      setPreparing(false);
    }
  };

  const copyToClipboard = (text: string, field: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading Job & Career Intelligence...</div>;
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Job Opportunity Intelligence</h2>
        <p className="text-sm text-slate-400 mt-1">
          Automated recruitment detection, recruiter trust scoring, and mathematical resume-matching.
        </p>
      </div>

      {/* Jobs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {jobs.map(job => {
          const match: JobMatch | undefined = job.matches && job.matches.length > 0 ? job.matches[0] : undefined;
          const matchScore = match?.match_score ?? 0;
          const isHighTrust = job.trust_level === 'LOW_RISK_SIGNALS';
          const isScamRisk = job.trust_level === 'HIGH_RISK_SIGNALS';

          return (
            <div
              key={job.id}
              className="rounded-2xl bg-slate-900/60 border border-slate-800 p-6 flex flex-col justify-between gap-5 hover:border-slate-700 transition"
            >
              <div className="space-y-4">
                {/* Header row */}
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">
                      {job.company}
                    </span>
                    <h3 className="text-lg font-bold text-white tracking-tight mt-0.5">{job.role}</h3>
                  </div>

                  {/* Job Match Score Badge */}
                  <div className="text-right shrink-0">
                    <div className="text-xl font-extrabold text-emerald-400">{matchScore}%</div>
                    <span className="text-[10px] text-slate-500 font-mono">Job Match Score</span>
                  </div>
                </div>

                {/* Metadata tags */}
                <div className="flex items-center gap-3 text-xs text-slate-400 flex-wrap">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-slate-500" />
                    {job.location} ({job.work_type})
                  </span>
                  {job.salary_range && (
                    <span className="flex items-center gap-1">
                      <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
                      {job.salary_range}
                    </span>
                  )}
                </div>

                {/* Trust / Risk Assessment Banner */}
                <div className={`p-3 rounded-xl border text-xs ${
                  isHighTrust
                    ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300'
                    : isScamRisk
                    ? 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                    : 'bg-amber-500/10 border-amber-500/20 text-amber-300'
                }`}>
                  <div className="flex items-center justify-between mb-1 font-semibold">
                    <span className="flex items-center gap-1.5">
                      {isHighTrust ? <ShieldCheck className="w-4 h-4 text-emerald-400" /> : <AlertTriangle className="w-4 h-4 text-rose-400" />}
                      {job.trust_level.replace(/_/g, ' ')}
                    </span>
                    <span className="font-mono">Trust: {job.trust_score}%</span>
                  </div>
                  <p className="text-[11px] opacity-90">
                    {job.trust_reasons.slice(0, 2).join(' · ')}
                  </p>
                </div>

                {/* Match Score Breakdown Bars */}
                {match && (
                  <div className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-700/40 space-y-2 text-xs">
                    <div className="flex justify-between text-[11px] text-slate-400 font-semibold mb-1">
                      <span>Formula Signal Breakdown</span>
                      <span className="font-mono text-indigo-400">Weighted Total</span>
                    </div>

                    <div className="space-y-1.5">
                      <div>
                        <div className="flex justify-between text-[11px] text-slate-300">
                          <span>Required Skills ({match.required_skill_match_pct}%)</span>
                          <span className="font-mono text-slate-400">Weight: 35%</span>
                        </div>
                        <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${match.required_skill_match_pct}%` }}></div>
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between text-[11px] text-slate-300">
                          <span>Semantic Similarity ({match.semantic_similarity_pct}%)</span>
                          <span className="font-mono text-slate-400">Weight: 20%</span>
                        </div>
                        <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div className="h-full bg-purple-500 rounded-full" style={{ width: `${match.semantic_similarity_pct}%` }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Matched vs Missing Skills */}
                {match && (
                  <div className="space-y-2 text-xs">
                    <div>
                      <span className="text-slate-400 font-medium">Matched Skills:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {match.matched_skills && match.matched_skills.length > 0 ? (
                          match.matched_skills.map(skill => (
                            <span key={skill} className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-[11px]">
                              ✓ {skill}
                            </span>
                          ))
                        ) : (
                          <span className="text-slate-500 text-[11px]">None</span>
                        )}
                      </div>
                    </div>

                    {match.missing_skills && match.missing_skills.length > 0 && (
                      <div>
                        <span className="text-slate-400 font-medium">Missing Skills:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {match.missing_skills.map(skill => (
                            <span key={skill} className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20 text-[11px]">
                              ✗ {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="pt-4 border-t border-slate-800 flex items-center justify-between gap-3">
                {job.application_url ? (
                  <a
                    href={job.application_url}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 font-medium"
                  >
                    <span>View Portal</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                ) : (
                  <span className="text-xs text-slate-500 italic">No direct link</span>
                )}

                <button
                  onClick={() => handlePrepareApplication(job)}
                  className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20 transition"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Prepare Application Pack</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Application Preparation Modal */}
      {selectedJob && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-3xl w-full p-6 space-y-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-xs font-semibold text-indigo-400 uppercase">Application Preparation Assistant</span>
                <h3 className="text-lg font-bold text-white mt-0.5">
                  {selectedJob.role} at {selectedJob.company}
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Human-in-the-loop: Review and edit tailored content before submitting. Never auto-submitted.
                </p>
              </div>
              <button
                onClick={() => { setSelectedJob(null); setApplicationPack(null); }}
                className="text-slate-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            {preparing ? (
              <div className="py-16 text-center text-slate-400">Synthesizing tailored application pack...</div>
            ) : applicationPack ? (
              <div className="space-y-5 text-xs text-slate-300">
                {/* Cover Letter */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                      <FileText className="w-4 h-4 text-indigo-400" /> Tailored Cover Letter
                    </span>
                    <button
                      onClick={() => copyToClipboard(applicationPack.cover_letter, 'cover')}
                      className="text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium"
                    >
                      <Copy className="w-3.5 h-3.5" />
                      <span>{copiedField === 'cover' ? 'Copied!' : 'Copy'}</span>
                    </button>
                  </div>
                  <textarea
                    rows={8}
                    value={applicationPack.cover_letter}
                    readOnly
                    className="w-full p-3 bg-slate-950/60 border border-slate-800 rounded-xl font-mono text-slate-300 leading-relaxed focus:outline-none"
                  ></textarea>
                </div>

                {/* Recruiter Outreach Note */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                      <Send className="w-4 h-4 text-purple-400" /> Recruiter LinkedIn / Email Pitch
                    </span>
                    <button
                      onClick={() => copyToClipboard(applicationPack.recruiter_pitch, 'pitch')}
                      className="text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium"
                    >
                      <Copy className="w-3.5 h-3.5" />
                      <span>{copiedField === 'pitch' ? 'Copied!' : 'Copy'}</span>
                    </button>
                  </div>
                  <textarea
                    rows={3}
                    value={applicationPack.recruiter_pitch}
                    readOnly
                    className="w-full p-3 bg-slate-950/60 border border-slate-800 rounded-xl font-mono text-slate-300 leading-relaxed focus:outline-none"
                  ></textarea>
                </div>

                {/* Interview Prep Q&A */}
                {applicationPack.interview_qa && (
                  <div className="space-y-3">
                    <span className="font-semibold text-slate-200">Interview Anticipated Questions & Talking Points</span>
                    <div className="space-y-2">
                      {applicationPack.interview_qa.map((qa: any, idx: number) => (
                        <div key={idx} className="p-3 rounded-xl bg-slate-950/40 border border-slate-800 space-y-1">
                          <div className="font-semibold text-slate-300">Q: {qa.question}</div>
                          <div className="text-slate-400 italic">Suggestion: {qa.suggested_answer}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : null}

            <div className="pt-4 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => { setSelectedJob(null); setApplicationPack(null); }}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
