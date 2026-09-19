export interface ExtractedEntity {
  id: string;
  entity_type: string;
  entity_value: string;
  confidence: number;
  metadata_json: Record<string, any>;
}

export interface EmailAnalysis {
  id: string;
  category: string;
  importance: number;
  urgency: number;
  actionability: number;
  storage_waste_score: number;
  is_promotional: boolean;
  is_job_related: boolean;
  security_risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  security_risk_reasons: string[];
  summary: string;
  raw_analysis: Record<string, any>;
  analyzed_at: string;
}

export interface EmailItem {
  id: string;
  thread_id: string;
  message_id_external: string;
  sender: string;
  sender_name?: string;
  recipients: string[];
  subject: string;
  body_text: string;
  body_html?: string;
  received_at: string;
  labels: string[];
  size_bytes: number;
  has_attachments: boolean;
  attachment_metadata: Array<{ filename: string; size_bytes: number; content_type?: string }>;
  processing_status: string;
  analysis?: EmailAnalysis;
  entities: ExtractedEntity[];
}

export interface TaskItem {
  id: string;
  email_id: string;
  title: string;
  description?: string;
  deadline?: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  status: 'OPEN' | 'PROMISED' | 'COMPLETED' | 'OVERDUE' | 'CANCELLED';
  confidence: number;
  created_at: string;
}

export interface CommitmentItem {
  id: string;
  email_id: string;
  statement: string;
  owner: string;
  deadline?: string;
  state: 'OPEN' | 'PROMISED' | 'COMPLETED' | 'OVERDUE' | 'CANCELLED';
  evidence_email_id?: string;
  last_state_change_at: string;
  created_at: string;
}

export interface JobSkill {
  id: string;
  skill_name: string;
  skill_type: 'REQUIRED' | 'PREFERRED';
  category: string;
}

export interface JobMatch {
  id: string;
  job_id: string;
  resume_id: string;
  match_score: number;
  required_skill_match_pct: number;
  preferred_skill_match_pct: number;
  semantic_similarity_pct: number;
  experience_match_pct: number;
  education_match_pct: number;
  matched_skills: string[];
  missing_skills: string[];
  prepared_application: Record<string, any>;
  calculated_at: string;
}

export interface JobItem {
  id: string;
  email_id: string;
  company: string;
  role: string;
  location: string;
  work_type: string;
  salary_range?: string;
  experience_years: number;
  education?: string;
  application_url?: string;
  deadline?: string;
  recruiter_email?: string;
  trust_score: number;
  trust_level: 'LOW_RISK_SIGNALS' | 'REVIEW_REQUIRED' | 'HIGH_RISK_SIGNALS';
  trust_reasons: string[];
  raw_description: string;
  created_at: string;
  skills: JobSkill[];
  matches: JobMatch[];
}

export interface ResumeSkill {
  id: string;
  skill_name: string;
  category: string;
  proficiency_level: string;
}

export interface ResumeProfile {
  id: string;
  full_name: string;
  summary?: string;
  raw_text: string;
  experience_years: number;
  education_level?: string;
  updated_at: string;
  skills: ResumeSkill[];
}

export interface StorageItem {
  email_id: string;
  subject: string;
  sender: string;
  received_at: string;
  size_bytes: number;
  waste_score: number;
  category: string;
  is_promotional: boolean;
  is_duplicate: boolean;
  reasons: string[];
  recommended_action: string;
}

export interface DuplicateGroup {
  group_id: string;
  canonical_email_id: string;
  canonical_subject: string;
  similarity_score: number;
  duplicate_email_ids: string[];
  total_size_bytes: number;
}

export interface StorageOverview {
  total_emails: number;
  total_storage_bytes: number;
  recoverable_storage_bytes: number;
  average_waste_score: number;
  promotional_count: number;
  duplicate_count: number;
  large_attachments_count: number;
  items: StorageItem[];
  duplicate_groups: DuplicateGroup[];
}

export interface ApprovalItem {
  id: string;
  recommendation_id: string;
  action_type: string;
  target_resource: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  reason: string;
  evidence: Record<string, any>;
  consequences?: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'EDITED';
  user_comments?: string;
  created_at: string;
  reviewed_at?: string;
}

export interface CalendarEventItem {
  id: string;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  location?: string;
  attendees: string[];
  status: string;
  google_event_id?: string;
}

export interface AuditLogItem {
  id: string;
  user_id: string;
  event_type: string;
  target_resource: string;
  action_taken: string;
  reason?: string;
  performed_by: string;
  metadata_json: Record<string, any>;
  timestamp: string;
}

export interface DashboardSummary {
  kpis: {
    unread_important: number;
    action_required: number;
    overdue_tasks: number;
    upcoming_deadlines: number;
    average_waste_score: number;
    recoverable_mb: number;
    job_opportunities: number;
    high_match_jobs: number;
    pending_approvals: number;
  };
  charts: {
    categories: Array<{ category: string; count: number }>;
    task_statuses: Array<{ status: string; count: number }>;
    storage_waste: Array<{ name: string; count: number }>;
  };
  recent_urgent: Array<{
    id: string;
    subject: string;
    sender: string;
    category: string;
    urgency: number;
    importance: number;
    received_at: string;
  }>;
  top_jobs: Array<{
    id: string;
    role: string;
    company: string;
    match_score: number;
    trust_score: number;
    trust_level: string;
  }>;
}
