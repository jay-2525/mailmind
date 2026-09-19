import React, { useState } from 'react';
import {
  GraduationCap,
  Play,
  CheckCircle2,
  Code2,
  Cpu,
  Shield,
  Layers,
  Sparkles,
  ArrowRight,
  Database
} from 'lucide-react';
import { api } from '../services/api';

interface StepCard {
  id: string;
  name: string;
  category: string;
  formula?: string;
  description: string;
  defaultInput: Record<string, any>;
}

export const AcademicDemo: React.FC = () => {
  const [activeStep, setActiveStep] = useState<string>('waste_score');
  const [stepInput, setStepInput] = useState<string>('');
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any | null>(null);

  const steps: StepCard[] = [
    {
      id: 'waste_score',
      name: 'Storage Waste Score Formula',
      category: 'Storage Intelligence',
      formula: 'Waste Score = min(100, max(0, sum(w_i * s_i) - sum(v_j * p_j)))',
      description: 'Multi-criteria decision formula penalizing size, redundancy, age, and promotional attributes while rewarding actionability.',
      defaultInput: {
        size_bytes: 25165824, // 24 MB
        is_promotional: true,
        redundancy_score: 0.92,
        has_tasks: false,
        has_commitments: false
      }
    },
    {
      id: 'job_matching',
      name: 'Job Match Scoring Engine',
      category: 'Career Intelligence',
      formula: '0.35 * S_req + 0.15 * S_pref + 0.20 * S_sem + 0.15 * S_exp + 0.15 * S_edu',
      description: 'Combines explicit skill set coverage, experience ratios, education tiers, and dense vector semantic cosine similarity.',
      defaultInput: {
        required_skills: ['Java', 'Python', 'SQL', 'Git'],
        candidate_skills: ['Java', 'Python', 'SQL', 'Git', 'React', 'FastAPI'],
        job_exp: 1.0,
        candidate_exp: 1.5,
        job_edu: 'Bachelor of Technology in CS',
        candidate_edu: 'Bachelor of Technology in CS'
      }
    },
    {
      id: 'duplicate_detection',
      name: 'Semantic Redundancy & Cosine Similarity',
      category: 'NLP & Embeddings',
      formula: 'cos(A, B) = (A · B) / (||A|| * ||B||)',
      description: 'Evaluates normalized subject lines, sender domains, and dense sentence embeddings to detect duplicate emails.',
      defaultInput: {
        subject_a: 'Mega Cloud Hosting Clearance - 80% OFF',
        subject_b: 'Fwd: Mega Cloud Hosting Clearance - 80% OFF',
        text_a: 'Unbeatable flash sale for cloud instances this weekend only!',
        text_b: 'Unbeatable flash sale for cloud instances this weekend only!'
      }
    },
    {
      id: 'trust_analysis',
      name: 'Recruiter Trust & Scam Analysis',
      category: 'Security & Safety',
      formula: 'Trust Score = 100 - sum(Risk Penalties)',
      description: 'Scans for advance-fee scams, fake check reimbursement patterns, free webmail impersonation, and phishing URLs.',
      defaultInput: {
        sender: 'hiring.manager.careers@gmail.com',
        company: 'Global Logistics Inc',
        body: 'Immediate hire! A cashier check of $2,500 will be mailed for home equipment. Wire transfer remainder via Bitcoin or Western Union.'
      }
    },
    {
      id: 'commitment_fsm',
      name: 'Commitment Finite State Machine (FSM)',
      category: 'State Tracking',
      formula: 'OPEN -> PROMISED -> COMPLETED / OVERDUE',
      description: 'Finite state machine validating valid lifecycle transitions for promises extracted from email conversations.',
      defaultInput: {
        current_state: 'PROMISED',
        new_state: 'COMPLETED'
      }
    },
    {
      id: 'ner',
      name: 'Named Entity Recognition (NER)',
      category: 'Information Extraction',
      description: 'Lexical parsing extracting organizations, person names, URLs, monetary amounts, and deadlines.',
      defaultInput: {
        text: 'Please submit the final distributed systems project to Prof. David Roberts at university.edu by Friday 5:00 PM for $500 lab credit.'
      }
    },
    {
      id: 'temporal',
      name: 'Temporal & Deadline Extraction',
      category: 'Information Extraction',
      description: 'Parses explicit calendar dates and relative temporal tokens (tomorrow, next Friday at 5 PM).',
      defaultInput: {
        text: 'The paper revision is due this Friday at 5:00 PM.'
      }
    },
    {
      id: 'safety_policy',
      name: 'Safety & Prompt Injection Defense',
      category: 'Security & Policy',
      description: 'Treats email content as strictly untrusted input and prevents command execution or prompt-injection jailbreaks.',
      defaultInput: {
        action: 'DELETE',
        prompt_injection: true
      }
    },
    {
      id: 'langgraph',
      name: 'LangGraph Agent State Machine',
      category: 'Agent Orchestration',
      description: 'End-to-end multi-node state graph orchestrating ingestion, context retrieval, multi-signal analysis, and policy gating.',
      defaultInput: {
        subject: 'Urgent meeting on project architecture',
        body: 'Please connect tomorrow at 3 PM to review the final code before the presentation.',
        sender: 'priya.sharma@techcorp.io'
      }
    }
  ];

  const currentStepCard = steps.find(s => s.id === activeStep) || steps[0];

  const handleSelectStep = (stepId: string) => {
    setActiveStep(stepId);
    const s = steps.find(x => x.id === stepId);
    if (s) {
      setStepInput(JSON.stringify(s.defaultInput, null, 2));
      setResult(null);
    }
  };

  const handleRun = async () => {
    setRunning(true);
    try {
      let parsedInput = currentStepCard.defaultInput;
      if (stepInput.trim()) {
        parsedInput = JSON.parse(stepInput);
      }
      const res = await api.runAcademicStep(activeStep, parsedInput);
      setResult(res);
    } catch (e: any) {
      alert(`Execution Error: ${e.message}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-wider mb-1">
          <GraduationCap className="w-4 h-4" />
          <span>B.Tech Project Review & Viva Defense Mode</span>
        </div>
        <h2 className="text-2xl font-bold text-white tracking-tight">
          Algorithm Transparency & Demonstration Sandbox
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          Inspect, test, and explain every individual AI, ML, NLP, and decision algorithm with live mathematical outputs.
        </p>
      </div>

      {/* Step Selector Pills */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5">
        {steps.map(s => (
          <button
            key={s.id}
            onClick={() => handleSelectStep(s.id)}
            className={`p-3 rounded-xl border text-left transition ${
              activeStep === s.id
                ? 'bg-amber-500/10 border-amber-500/40 text-amber-300 shadow-sm'
                : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            <span className="text-[10px] font-mono uppercase text-slate-500 block mb-1">{s.category}</span>
            <span className="text-xs font-bold block truncate">{s.name}</span>
          </button>
        ))}
      </div>

      {/* Active Step Interactive Sandbox */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Configuration & Input */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div>
            <span className="text-xs font-mono uppercase text-amber-400 font-semibold">{currentStepCard.category}</span>
            <h3 className="text-lg font-bold text-white mt-0.5">{currentStepCard.name}</h3>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">{currentStepCard.description}</p>
          </div>

          {currentStepCard.formula && (
            <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 font-mono text-xs text-indigo-300">
              <span className="text-[10px] text-slate-500 block uppercase mb-0.5">Mathematical Formulation:</span>
              {currentStepCard.formula}
            </div>
          )}

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
              <span>Interactive Test Input (JSON):</span>
              <button
                onClick={() => setStepInput(JSON.stringify(currentStepCard.defaultInput, null, 2))}
                className="text-[11px] text-indigo-400 hover:text-indigo-300 font-normal"
              >
                Reset Default
              </button>
            </label>
            <textarea
              rows={9}
              value={stepInput || JSON.stringify(currentStepCard.defaultInput, null, 2)}
              onChange={e => setStepInput(e.target.value)}
              className="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl font-mono text-xs text-slate-300 focus:outline-none focus:border-amber-500 leading-relaxed"
            ></textarea>
          </div>

          <button
            onClick={handleRun}
            disabled={running}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs shadow-lg shadow-amber-500/20 transition disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{running ? 'Executing Algorithm...' : 'Execute Algorithm & Inspect Output'}</span>
          </button>
        </div>

        {/* Right: Step-by-Step Mathematical Output */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <Cpu className="w-4 h-4 text-emerald-400" />
                Algorithm Output & Intermediate State
              </h4>
              {result && (
                <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-mono font-bold">
                  200 OK
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400">
              Live mathematical breakdown showing intermediate weights, vector cosine steps, or state decisions.
            </p>
          </div>

          <div className="flex-1 min-h-[300px]">
            {result ? (
              <pre className="p-4 bg-slate-950/90 border border-slate-800 rounded-xl font-mono text-xs text-slate-200 overflow-x-auto max-h-[380px] overflow-y-auto leading-relaxed">
                {JSON.stringify(result, null, 2)}
              </pre>
            ) : (
              <div className="h-full min-h-[250px] flex flex-col items-center justify-center border border-dashed border-slate-800 rounded-xl text-slate-500 text-xs gap-2">
                <Code2 className="w-6 h-6 text-slate-600" />
                <span>Click "Execute Algorithm" to view live intermediate calculations.</span>
              </div>
            )}
          </div>

          {result && (
            <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400 shrink-0" />
              <span>
                Demonstrated real backend execution of {currentStepCard.name} using real Python ML/NLP services.
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
