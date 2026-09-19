import React, { useState, useEffect } from 'react';
import {
  Calendar as CalendarIcon,
  Clock,
  MapPin,
  Users,
  CheckCircle2,
  ExternalLink,
  ShieldAlert
} from 'lucide-react';
import { CalendarEventItem } from '../types';
import { api } from '../services/api';

export const CalendarView: React.FC = () => {
  const [events, setEvents] = useState<CalendarEventItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [pushingId, setPushingId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const loadEvents = async () => {
    setLoading(true);
    try {
      const data = await api.getCalendarEvents();
      setEvents(data);
    } catch (e) {
      console.error('Failed to load calendar events:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvents();
  }, []);

  const handlePush = async (eventId: string) => {
    setPushingId(eventId);
    try {
      const res = await api.pushCalendarEvent(eventId);
      setMessage(res.message);
      setTimeout(() => setMessage(null), 4000);
      loadEvents();
    } catch (e: any) {
      alert(`Could not push event: ${e.message}`);
    } finally {
      setPushingId(null);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading Google Calendar Events...</div>;
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Google Calendar Intelligence</h2>
        <p className="text-sm text-slate-400 mt-1">
          Extracted meetings and scheduling assistance with conflict detection and human approval.
        </p>
      </div>

      {message && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{message}</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {events.length === 0 ? (
          <div className="col-span-2 p-12 text-center rounded-2xl bg-slate-900/40 border border-slate-800 text-slate-400">
            No meeting invitations currently detected.
          </div>
        ) : (
          events.map(event => {
            const isConfirmed = event.status === 'CONFIRMED';
            return (
              <div
                key={event.id}
                className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4 hover:border-slate-700 transition"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                      isConfirmed
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-amber-500/10 text-amber-300 border border-amber-500/20'
                    }`}>
                      {event.status}
                    </span>
                    <h3 className="text-base font-bold text-white tracking-tight mt-1.5">{event.title}</h3>
                  </div>

                  <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shrink-0">
                    <CalendarIcon className="w-5 h-5" />
                  </div>
                </div>

                <div className="space-y-2 text-xs text-slate-300">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-slate-500" />
                    <span>
                      {new Date(event.start_time).toLocaleString(undefined, {
                        weekday: 'short',
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })} - {new Date(event.end_time).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>

                  {event.location && (
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-slate-500" />
                      <span className="truncate">{event.location}</span>
                    </div>
                  )}

                  {event.description && (
                    <p className="text-slate-400 text-[11px] pt-1 italic">
                      "{event.description}"
                    </p>
                  )}
                </div>

                <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                  <span className="text-[11px] text-slate-500 font-mono">
                    Google Calendar API
                  </span>

                  {!isConfirmed ? (
                    <button
                      onClick={() => handlePush(event.id)}
                      disabled={pushingId === event.id}
                      className="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition disabled:opacity-50"
                    >
                      {pushingId === event.id ? 'Scheduling...' : 'Approve & Push to Calendar'}
                    </button>
                  ) : (
                    <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Scheduled
                    </span>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
