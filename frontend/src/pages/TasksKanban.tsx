import React, { useState, useEffect } from 'react';
import {
  CheckSquare,
  Clock,
  AlertCircle,
  CheckCircle2,
  Calendar,
  Flag,
  ArrowRight,
  ShieldCheck,
  Plus
} from 'lucide-react';
import { TaskItem, CommitmentItem } from '../types';
import { api } from '../services/api';

export const TasksKanban: React.FC = () => {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [commitments, setCommitments] = useState<CommitmentItem[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [tData, cData] = await Promise.all([api.getTasks(), api.getCommitments()]);
      setTasks(tData);
      setCommitments(cData);
    } catch (e) {
      console.error('Failed to load tasks/commitments:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleTaskStatusChange = async (taskId: string, newStatus: TaskItem['status']) => {
    try {
      await api.updateTask(taskId, { status: newStatus });
      loadData();
    } catch (e: any) {
      alert(`Could not update task: ${e.message}`);
    }
  };

  const handleCommitmentStateChange = async (commitmentId: string, newState: string) => {
    try {
      await api.updateCommitmentState(commitmentId, newState);
      loadData();
    } catch (e: any) {
      alert(`Invalid FSM transition: ${e.message}`);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading Personal Task & Commitment Manager...</div>;
  }

  // Combined item format for kanban
  type KanbanCard = {
    id: string;
    title: string;
    deadline?: string;
    priority?: string;
    status: string;
    confidence: number;
    kind: 'TASK' | 'COMMITMENT';
    owner?: string;
  };

  const allCards: KanbanCard[] = [
    ...tasks.map(t => ({
      id: t.id,
      title: t.title,
      deadline: t.deadline,
      priority: t.priority,
      status: t.status,
      confidence: t.confidence,
      kind: 'TASK' as const
    })),
    ...commitments.map(c => ({
      id: c.id,
      title: c.statement,
      deadline: c.deadline,
      priority: 'HIGH',
      status: c.state,
      confidence: 0.95,
      kind: 'COMMITMENT' as const,
      owner: c.owner
    }))
  ];

  const columns = [
    { id: 'OPEN', label: 'Open Tasks', color: 'border-indigo-500/30 text-indigo-400' },
    { id: 'PROMISED', label: 'Promised Commitments', color: 'border-amber-500/30 text-amber-400' },
    { id: 'OVERDUE', label: 'Overdue Attention', color: 'border-rose-500/30 text-rose-400' },
    { id: 'COMPLETED', label: 'Completed', color: 'border-emerald-500/30 text-emerald-400' },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Personal Task & Commitment Manager</h2>
        <p className="text-sm text-slate-400 mt-1">
          Automated action extraction and Finite State Machine (FSM) commitment lifecycle tracking.
        </p>
      </div>

      {/* Kanban Board Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {columns.map(col => {
          const colCards = allCards.filter(c => c.status === col.id);
          return (
            <div key={col.id} className="space-y-3">
              {/* Column Header */}
              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${
                    col.id === 'OPEN' ? 'bg-indigo-400' :
                    col.id === 'PROMISED' ? 'bg-amber-400' :
                    col.id === 'OVERDUE' ? 'bg-rose-400' : 'bg-emerald-400'
                  }`}></span>
                  <span className="text-xs font-bold text-slate-200">{col.label}</span>
                </div>
                <span className="px-2 py-0.5 rounded-full bg-slate-800 text-[11px] font-mono text-slate-400">
                  {colCards.length}
                </span>
              </div>

              {/* Cards List */}
              <div className="space-y-3 min-h-[400px]">
                {colCards.length === 0 ? (
                  <div className="p-8 text-center rounded-xl border border-dashed border-slate-800 text-xs text-slate-600">
                    No items in this state.
                  </div>
                ) : (
                  colCards.map(card => {
                    const isOverdue = col.id === 'OVERDUE';
                    return (
                      <div
                        key={`${card.kind}-${card.id}`}
                        className={`p-4 rounded-xl bg-slate-900/80 border transition hover:border-slate-700 flex flex-col justify-between gap-3 ${
                          isOverdue ? 'border-rose-500/40' : 'border-slate-800'
                        }`}
                      >
                        <div className="space-y-2">
                          <div className="flex items-center justify-between gap-2">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                              card.kind === 'COMMITMENT'
                                ? 'bg-purple-500/10 text-purple-300 border border-purple-500/20'
                                : 'bg-blue-500/10 text-blue-300 border border-blue-500/20'
                            }`}>
                              {card.kind} {card.owner ? `(${card.owner})` : ''}
                            </span>

                            {card.priority && (
                              <span className={`text-[10px] font-semibold ${
                                card.priority === 'HIGH' || card.priority === 'URGENT'
                                  ? 'text-rose-400'
                                  : 'text-slate-400'
                              }`}>
                                {card.priority}
                              </span>
                            )}
                          </div>

                          <p className="text-xs font-semibold text-slate-200 leading-snug">
                            {card.title}
                          </p>

                          {card.deadline && (
                            <div className="flex items-center gap-1 text-[11px] text-slate-400">
                              <Clock className="w-3 h-3 text-slate-500" />
                              <span>Due: {new Date(card.deadline).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
                            </div>
                          )}
                        </div>

                        {/* State Transition Actions */}
                        <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
                          <span className="text-[10px] font-mono text-slate-500">
                            Conf: {Math.round(card.confidence * 100)}%
                          </span>

                          <div className="flex items-center gap-1.5">
                            {col.id !== 'COMPLETED' ? (
                              <button
                                onClick={() =>
                                  card.kind === 'TASK'
                                    ? handleTaskStatusChange(card.id, 'COMPLETED')
                                    : handleCommitmentStateChange(card.id, 'COMPLETED')
                                }
                                className="px-2 py-1 rounded bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 text-[10px] font-semibold border border-emerald-500/20 transition flex items-center gap-1"
                              >
                                <CheckCircle2 className="w-3 h-3" />
                                <span>Complete</span>
                              </button>
                            ) : (
                              <button
                                onClick={() =>
                                  card.kind === 'TASK'
                                    ? handleTaskStatusChange(card.id, 'OPEN')
                                    : handleCommitmentStateChange(card.id, 'OPEN')
                                }
                                className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] transition"
                              >
                                Reopen
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
