import {
  DashboardSummary,
  EmailItem,
  StorageOverview,
  TaskItem,
  CommitmentItem,
  JobItem,
  JobMatch,
  ResumeProfile,
  ApprovalItem,
  CalendarEventItem,
  AuditLogItem
} from '../types';

const API_BASE = '/api/v1';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('inboxguard_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options?.headers as Record<string, string>),
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Request failed with status ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Auth
  demoLogin: () => fetchJson<{ access_token: string; user: any }>(`${API_BASE}/auth/demo`, { method: 'POST' }),
  getCurrentUser: () => fetchJson<any>(`${API_BASE}/auth/me`),
  getGoogleAuthUrl: () => fetchJson<{ auth_url: string; is_demo: boolean }>(`${API_BASE}/auth/google/url`),

  // Dashboard
  getDashboardSummary: () => fetchJson<DashboardSummary>(`${API_BASE}/dashboard/summary`),

  // Emails
  getEmails: (category?: string, search?: string) => {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (search) params.append('search', search);
    return fetchJson<EmailItem[]>(`${API_BASE}/emails?${params.toString()}`);
  },
  getEmailDetail: (id: string) => fetchJson<EmailItem>(`${API_BASE}/emails/${id}`),
  syncEmails: () => fetchJson<{ processed_count: number; message: string }>(`${API_BASE}/emails/sync`, { method: 'POST' }),

  // Storage
  getStorageOverview: () => fetchJson<StorageOverview>(`${API_BASE}/storage/overview`),
  stageStorageCleanup: (email_ids: string[], action: 'ARCHIVE' | 'DELETE') =>
    fetchJson<any>(`${API_BASE}/storage/cleanup`, {
      method: 'POST',
      body: JSON.stringify({ email_ids, action }),
    }),

  // Tasks & Commitments
  getTasks: (status?: string) => {
    const url = status ? `${API_BASE}/tasks?status=${status}` : `${API_BASE}/tasks`;
    return fetchJson<TaskItem[]>(url);
  },
  updateTask: (id: string, updates: Partial<TaskItem>) =>
    fetchJson<TaskItem>(`${API_BASE}/tasks/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    }),
  getCommitments: (state?: string) => {
    const url = state ? `${API_BASE}/tasks/commitments?state=${state}` : `${API_BASE}/tasks/commitments`;
    return fetchJson<CommitmentItem[]>(url);
  },
  updateCommitmentState: (id: string, state: string) =>
    fetchJson<CommitmentItem>(`${API_BASE}/tasks/commitments/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ state }),
    }),

  // Jobs
  getJobs: () => fetchJson<JobItem[]>(`${API_BASE}/jobs`),
  getJobDetail: (id: string) => fetchJson<JobItem>(`${API_BASE}/jobs/${id}`),
  recalculateJobMatch: (jobId: string) =>
    fetchJson<JobMatch>(`${API_BASE}/jobs/${jobId}/match`, { method: 'POST' }),
  prepareJobApplication: (jobId: string, customNotes?: string) =>
    fetchJson<any>(`${API_BASE}/jobs/${jobId}/prepare-application`, {
      method: 'POST',
      body: JSON.stringify({ custom_notes: customNotes }),
    }),

  // Resume
  getResume: () => fetchJson<ResumeProfile>(`${API_BASE}/resume`),
  uploadResumeText: (text: string) => {
    const formData = new FormData();
    formData.append('resume_text', text);
    const token = localStorage.getItem('inboxguard_token');
    return fetch(`${API_BASE}/resume/upload`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    }).then(res => res.json());
  },
  addResumeSkill: (skill_name: string, category: string = 'Technical') =>
    fetchJson<any>(`${API_BASE}/resume/skills`, {
      method: 'POST',
      body: JSON.stringify({ skill_name, category }),
    }),
  deleteResumeSkill: (skillId: string) =>
    fetchJson<any>(`${API_BASE}/resume/skills/${skillId}`, { method: 'DELETE' }),

  // Approvals
  getApprovals: (status: string = 'PENDING') =>
    fetchJson<ApprovalItem[]>(`${API_BASE}/approvals?status=${status}`),
  actOnApproval: (approvalId: string, action: 'APPROVE' | 'REJECT' | 'EDIT', user_comments?: string) =>
    fetchJson<any>(`${API_BASE}/approvals/${approvalId}/action`, {
      method: 'POST',
      body: JSON.stringify({ action, user_comments }),
    }),

  // Calendar
  getCalendarEvents: () => fetchJson<CalendarEventItem[]>(`${API_BASE}/calendar/events`),
  pushCalendarEvent: (eventId: string) =>
    fetchJson<any>(`${API_BASE}/calendar/events/${eventId}/push`, { method: 'POST' }),

  // RAG
  searchRAG: (query: string, categoryFilter?: string) =>
    fetchJson<any>(`${API_BASE}/rag/search`, {
      method: 'POST',
      body: JSON.stringify({ query, category_filter: categoryFilter }),
    }),

  // Audit Logs
  getAuditLogs: (limit: number = 100) =>
    fetchJson<AuditLogItem[]>(`${API_BASE}/audit/logs?limit=${limit}`),

  // Demo Controls
  getDemoStatus: () => fetchJson<any>(`${API_BASE}/demo/status`),
  resetDemoData: () => fetchJson<any>(`${API_BASE}/demo/reset`, { method: 'POST' }),

  // Academic Viva Sandbox
  runAcademicStep: (stepName: string, inputData: Record<string, any>) =>
    fetchJson<any>(`${API_BASE}/academic-demo/pipeline-step`, {
      method: 'POST',
      body: JSON.stringify({ step_name: stepName, input_data: inputData }),
    }),
};
