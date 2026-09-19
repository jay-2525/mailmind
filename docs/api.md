# REST API Reference: MailMind (InboxGuard)

> **Base URL**: `http://localhost:8000/api/v1`  
> **Interactive Swagger UI**: `http://localhost:8000/docs`  
> **ReDoc**: `http://localhost:8000/redoc`  
> **Authentication**: `Authorization: Bearer <JWT_TOKEN>` (Optional in demo mode)

---

## 1. Authentication & Session Management (`/auth`)

### `GET /auth/me`
Fetches the currently active user profile, synced status, and preferences.

**Response (`200 OK`)**:
```json
{
  "id": "c830a36e-d284-4860-93cb-66b26cf9d846",
  "email": "doremonhaaa@gmail.com",
  "full_name": "Doremon",
  "is_demo": false,
  "preferences": {
    "theme": "dark",
    "auto_analyze": true
  }
}
```

---

### `POST /auth/switch-mode`
Toggles the active session between **Personal Gmail** and **Academic Demo Mode**.

**Request Body**:
```json
{
  "mode": "personal" // or "demo"
}
```

**Response (`200 OK`)**:
```json
{
  "status": "SUCCESS",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "c830a36e-d284-4860-93cb-66b26cf9d846",
    "email": "doremonhaaa@gmail.com",
    "full_name": "Doremon",
    "is_demo": false
  }
}
```

---

## 2. Dashboard Intelligence (`/dashboard`)

### `GET /dashboard/summary`
Returns aggregated Key Performance Indicators (KPIs), category distributions, waste charts, urgent emails, and top career opportunities.

**Response (`200 OK`)**:
```json
{
  "kpis": {
    "unread_important": 5,
    "action_required": 2,
    "overdue_tasks": 0,
    "upcoming_deadlines": 2,
    "average_waste_score": 25.7,
    "recoverable_mb": 0.3,
    "job_opportunities": 2,
    "high_match_jobs": 1,
    "pending_approvals": 8
  },
  "charts": {
    "categories": [
      { "category": "Education", "count": 3 },
      { "category": "Meeting", "count": 1 },
      { "category": "Promotion", "count": 2 },
      { "category": "Job Opportunity", "count": 2 }
    ],
    "task_statuses": [
      { "status": "OPEN", "count": 3 },
      { "status": "PROMISED", "count": 1 },
      { "status": "COMPLETED", "count": 0 },
      { "status": "OVERDUE", "count": 0 }
    ],
    "storage_waste": [
      { "name": "Low Waste (0-40)", "count": 7 },
      { "name": "Moderate (41-70)", "count": 3 },
      { "name": "High Waste (71-100)", "count": 0 }
    ]
  },
  "recent_urgent": [
    {
      "id": "em_d57d59b20e06",
      "subject": "GATE 2026 CSE Shift 2 Question Paper OUT",
      "sender": "Careers360",
      "category": "Job Opportunity",
      "urgency": 0.85,
      "importance": 0.90,
      "received_at": "2026-09-19T04:22:15.358249Z"
    }
  ],
  "top_jobs": [
    {
      "id": "job_01",
      "role": "Software Engineer Intern",
      "company": "Google",
      "match_score": 88.5,
      "trust_score": 95.0,
      "trust_level": "VERIFIED"
    }
  ]
}
```

---

## 3. Storage Intelligence & Cleanup (`/storage`)

### `GET /storage/overview`
Returns itemized email storage analysis, computed waste scores, redundancy flags, and recoverable storage metrics.

**Response (`200 OK`)**:
```json
{
  "total_emails": 14,
  "total_storage_bytes": 1052400,
  "recoverable_storage_bytes": 354000,
  "average_waste_score": 25.7,
  "promotional_count": 2,
  "duplicate_count": 1,
  "large_attachments_count": 0,
  "items": [
    {
      "email_id": "em_c07ee974b62d",
      "subject": "Your Discord Login Link Has Arrived!",
      "sender": "Discord",
      "received_at": "2026-09-19T04:22:15.357116Z",
      "size_bytes": 354000,
      "waste_score": 92.0,
      "category": "Promotion",
      "is_promotional": true,
      "is_duplicate": true,
      "reasons": [
        "Single-use magic link / OTP pattern detected",
        "Exact semantic duplicate of earlier notification"
      ],
      "recommended_action": "DELETE"
    }
  ]
}
```

---

### `POST /storage/cleanup`
Executes either instant direct deletion or stages the destructive action in the Approval Center.

**Request Body**:
```json
{
  "email_ids": ["em_c07ee974b62d"],
  "action": "DELETE", // "DELETE" or "ARCHIVE"
  "requires_approval": false // false = instant direct delete; true = stage in HITL Approval Center
}
```

**Response (`200 OK`)**:
```json
{
  "action": "DELETE",
  "queued_for_approval": false,
  "affected_count": 1,
  "approval_id": null,
  "message": "Successfully deleted 1 email(s) immediately."
}
```

---

## 4. Tasks & Commitment FSM (`/tasks`)

### `GET /tasks`
Fetches tasks extracted by the NER and Temporal parsing engine.

**Query Parameters**:
- `status` *(optional)*: `OPEN`, `COMPLETED`

**Response (`200 OK`)**:
```json
[
  {
    "id": "task_01",
    "email_id": "em_d57d59b20e06",
    "title": "Verify Lovely Professional University Student Portal Link",
    "description": "Extracted from email: Complete your email verification in just one click",
    "deadline": "2026-09-21T18:00:00Z",
    "priority": "HIGH",
    "status": "OPEN",
    "confidence": 0.92
  }
]
```

---

### `GET /tasks/commitments`
Lists conversational commitments evaluated against the Finite State Machine (`OPEN` $\to$ `PROMISED` $\to$ `COMPLETED` / `OVERDUE`).

**Response (`200 OK`)**:
```json
[
  {
    "id": "commit_01",
    "email_id": "em_2b406ad23bb7",
    "statement": "Inquiry regarding special subscription pricing for Aha 4",
    "owner": "SELF",
    "deadline": "2026-09-22T17:00:00Z",
    "state": "PROMISED",
    "last_state_change_at": "2026-09-19T04:22:15.361543Z"
  }
]
```

---

### `PATCH /tasks/commitments/{commitment_id}`
Transitions commitment state. Enforces FSM transition validation rules.

**Request Body**:
```json
{
  "state": "COMPLETED" // "PROMISED", "COMPLETED", "OVERDUE", "CANCELLED"
}
```

---

## 5. Job Intelligence & Career Matching (`/jobs`)

### `GET /jobs`
Lists job postings extracted from recruitment emails, evaluated for legitimacy trust score and candidate skill match percentage.

**Response (`200 OK`)**:
```json
[
  {
    "id": "job_google_001",
    "company": "Google",
    "role": "Software Engineer Intern (Backend Systems)",
    "location": "Mountain View, CA / Hybrid",
    "work_type": "HYBRID",
    "salary_range": "$55 - $65 / hr",
    "trust_score": 95.0,
    "trust_level": "VERIFIED",
    "trust_reasons": ["Sender domain google.com matches corporate organization"],
    "matches": [
      {
        "match_score": 88.5,
        "required_skill_match_pct": 100.0,
        "preferred_skill_match_pct": 66.7,
        "semantic_similarity_pct": 84.2,
        "experience_match_pct": 100.0,
        "matched_skills": ["Python", "Java", "SQL", "Git", "REST APIs", "Docker"],
        "missing_skills": ["Kubernetes"]
      }
    ]
  }
]
```

---

### `POST /jobs/{job_id}/prepare-application`
Generates a tailored cover letter and recruiter outreach pitch based on matched skills without auto-submitting.

**Response (`200 OK`)**:
```json
{
  "cover_letter": "Dear University Recruiting Team at Google,\n\nI am writing to express my strong enthusiasm for the Software Engineer Intern role...",
  "recruiter_pitch": "Hi Google Recruiting! I saw your Software Engineer Intern opening in Backend Systems and wanted to introduce myself...",
  "interview_qa": [
    {
      "question": "How have you applied distributed systems principles in past projects?",
      "talking_point": "Discuss the LangGraph multi-agent orchestration and pgvector semantic retrieval pipeline built in MailMind."
    }
  ]
}
```

---

## 6. Human-in-the-Loop Approval Center (`/approvals`)

### `GET /approvals`
Lists actions held for mandatory user consent.

**Query Parameters**:
- `status` *(optional)*: `PENDING`, `APPROVED`, `REJECTED`

---

### `POST /approvals/{approval_id}/action`
Authorizes, rejects, or edits an action queued by the agent.

**Request Body**:
```json
{
  "action": "APPROVE", // "APPROVE" or "REJECT"
  "user_comments": "Authorized deletion of bulk expired promotional emails"
}
```

**Response (`200 OK`)**:
```json
{
  "approval_id": "appr_7c413b8e-6d4b",
  "status": "APPROVED",
  "execution_result": {
    "action": "DELETE",
    "affected_emails": 1,
    "status": "SUCCESS"
  },
  "message": "Action 'DELETE' was approved and executed successfully."
}
```

---

## 7. Historical Hybrid RAG (`/rag`)

### `POST /rag/search`
Performs hybrid search combining 384-dimensional dense vector embeddings with sparse keyword matching via Reciprocal Rank Fusion (RRF).

**Request Body**:
```json
{
  "query": "distributed systems assignment submission deadline",
  "top_k": 3
}
```

**Response (`200 OK`)**:
```json
{
  "query": "distributed systems assignment submission deadline",
  "total_results": 1,
  "results": [
    {
      "email_id": "msg_assignment_001",
      "subject": "CS401: Distributed Systems - Final Project Submission Deadline",
      "sender": "prof.roberts@university.edu",
      "dense_score": 0.892,
      "sparse_score": 0.781,
      "rrf_score": 0.0324,
      "explanation": "High semantic overlap regarding final project submission instructions and deadline parameters."
    }
  ]
}
```
