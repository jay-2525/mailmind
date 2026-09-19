import React, { useState, useEffect } from 'react';
import {
  FileText,
  Plus,
  Trash2,
  RefreshCw,
  Sparkles,
  Upload,
  CheckCircle2,
  GraduationCap
} from 'lucide-react';
import { ResumeProfile } from '../types';
import { api } from '../services/api';

export const ResumeView: React.FC = () => {
  const [profile, setProfile] = useState<ResumeProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [newSkill, setNewSkill] = useState('');
  const [newSkillCat, setNewSkillCat] = useState('Technical');
  const [resumeTextInput, setResumeTextInput] = useState('');
  const [updating, setUpdating] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const loadResume = async () => {
    setLoading(true);
    try {
      const data = await api.getResume();
      setProfile(data);
      setResumeTextInput(data.raw_text);
    } catch (e) {
      console.error('Failed to load resume:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadResume();
  }, []);

  const handleAddSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSkill.trim()) return;
    try {
      await api.addResumeSkill(newSkill.trim(), newSkillCat);
      setNewSkill('');
      loadResume();
    } catch (e: any) {
      alert(`Error adding skill: ${e.message}`);
    }
  };

  const handleDeleteSkill = async (id: string) => {
    try {
      await api.deleteResumeSkill(id);
      loadResume();
    } catch (e: any) {
      alert(`Error deleting skill: ${e.message}`);
    }
  };

  const handleUpdateResume = async () => {
    if (!resumeTextInput.trim()) return;
    setUpdating(true);
    try {
      const updated = await api.uploadResumeText(resumeTextInput);
      setProfile(updated);
      setMessage('Resume text parsed and vector embeddings updated successfully!');
      setTimeout(() => setMessage(null), 4000);
      loadResume();
    } catch (e: any) {
      alert(`Error updating resume: ${e.message}`);
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading Candidate Resume Profile...</div>;
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Candidate Resume & Skills</h2>
          <p className="text-sm text-slate-400 mt-1">
            Structured skill profile and dense vector embedding used for Job Match Scoring.
          </p>
        </div>
      </div>

      {message && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{message}</span>
        </div>
      )}

      {profile && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Profile & Skills */}
          <div className="lg:col-span-2 space-y-6">
            {/* Candidate Summary Card */}
            <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-white">{profile.full_name}</h3>
                  <div className="flex items-center gap-2 text-xs text-indigo-400 mt-0.5">
                    <GraduationCap className="w-3.5 h-3.5" />
                    <span>{profile.education_level || 'B.Tech in Computer Science'}</span>
                    <span>·</span>
                    <span>{profile.experience_years} Years Experience</span>
                  </div>
                </div>
                <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold">
                  Vector Embedded (384d)
                </span>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/40 p-3 rounded-xl border border-slate-800">
                {profile.summary}
              </p>
            </div>

            {/* Extracted Skills Management */}
            <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-bold text-white">Extracted Skills & Competencies</h4>
                <span className="text-xs font-mono text-slate-400">{profile.skills.length} skills indexed</span>
              </div>

              {/* Skills Tags */}
              <div className="flex flex-wrap gap-2">
                {profile.skills.map(skill => (
                  <span
                    key={skill.id}
                    className="group inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-800 border border-slate-700 text-xs font-medium text-slate-200"
                  >
                    <span>{skill.skill_name}</span>
                    <span className="text-[10px] text-slate-500 font-mono">({skill.category})</span>
                    <button
                      onClick={() => handleDeleteSkill(skill.id)}
                      className="text-slate-500 hover:text-rose-400 ml-1 transition"
                      title="Remove skill"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>

              {/* Add Custom Skill Form */}
              <form onSubmit={handleAddSkill} className="pt-3 border-t border-slate-800 flex items-center gap-3">
                <input
                  type="text"
                  value={newSkill}
                  onChange={e => setNewSkill(e.target.value)}
                  placeholder="Add skill (e.g. PyTorch, Kubernetes)..."
                  className="flex-1 px-3 py-1.5 bg-slate-950/60 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                />
                <select
                  value={newSkillCat}
                  onChange={e => setNewSkillCat(e.target.value)}
                  className="px-3 py-1.5 bg-slate-950/60 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none"
                >
                  <option value="Technical">Technical</option>
                  <option value="Framework">Framework</option>
                  <option value="Database">Database</option>
                  <option value="Cloud">Cloud</option>
                  <option value="Soft Skill">Soft Skill</option>
                </select>
                <button
                  type="submit"
                  className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add</span>
                </button>
              </form>
            </div>
          </div>

          {/* Right: Resume Text & Raw Parser */}
          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-bold text-white flex items-center gap-1.5">
                <FileText className="w-4 h-4 text-indigo-400" />
                Raw Resume Text
              </h4>
            </div>
            <p className="text-xs text-slate-400">
              Paste updated resume content below to automatically re-extract skills and generate updated embeddings.
            </p>

            <textarea
              rows={16}
              value={resumeTextInput}
              onChange={e => setResumeTextInput(e.target.value)}
              className="w-full p-3 bg-slate-950/80 border border-slate-800 rounded-xl font-mono text-xs text-slate-300 leading-relaxed focus:outline-none focus:border-indigo-500"
            ></textarea>

            <button
              onClick={handleUpdateResume}
              disabled={updating}
              className="w-full flex items-center justify-center gap-2 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${updating ? 'animate-spin' : ''}`} />
              <span>{updating ? 'Re-parsing Resume...' : 'Update & Re-embed Resume'}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
