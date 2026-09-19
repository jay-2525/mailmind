# REST API Documentation: MailMind (InboxGuard)

The InboxGuard backend provides OpenAPI-compliant REST endpoints under `/api/v1`. Interactive Swagger UI is accessible at `http://localhost:8000/docs`.

---

## Endpoint Reference

### 1. Authentication (`/api/v1/auth`)
- `GET /google/url`: Generate Google OAuth 2.0 authorization URL with least-privilege scopes.
- `GET /google/callback`: Handle OAuth redirect code, exchange tokens, and generate JWT.
- `POST /demo`: Instant one-click login for demo mode.
- `GET /me`: Return current user profile and preferences.

### 2. Emails & Threads (`/api/v1/emails`)
- `GET /`: List emails with category, search query, limit, and offset pagination.
- `GET /threads`: Fetch threaded email conversations.
- `GET /{id}`: Fetch full email details including extracted entities and multi-signal analysis.
- `POST /sync`: Ingest pending emails and dispatch them to the LangGraph decision pipeline.

### 3. Storage Intelligence (`/api/v1/storage`)
- `GET /overview`: Return total storage, recoverable storage, average waste score, duplicate groups, and itemized emails.
- `POST /cleanup`: Stage selected emails for `ARCHIVE` or `DELETE` in the Approval Center.

### 4. Tasks & Commitments (`/api/v1/tasks`)
- `GET /`: List tasks filtered by status (`OPEN`, `COMPLETED`).
- `POST /`: Create custom task.
- `PATCH /{id}`: Update task status, title, or deadline.
- `GET /commitments`: List commitments with FSM state evaluation (`OPEN`, `PROMISED`, `OVERDUE`, `COMPLETED`).
- `PATCH /commitments/{id}`: Update commitment state (strictly validated by FSM rules).

### 5. Career & Job Intelligence (`/api/v1/jobs`)
- `GET /`: List detected job postings with match scores and trust levels.
- `GET /{id}`: Fetch job details, required skills, and match breakdown.
- `POST /{id}/match`: Recalculate match score against candidate resume profile.
- `POST /{id}/prepare-application`: Generate tailored cover letter, recruiter pitch, and interview QA.

### 6. Resume Profile (`/api/v1/resume`)
- `GET /`: Return candidate resume profile and extracted skill list.
- `POST /upload`: Upload text or document to parse skills and generate 384d vector embedding.
- `POST /skills`: Add custom skill tag.
- `DELETE /skills/{id}`: Remove skill tag.

### 7. Historical RAG (`/api/v1/rag`)
- `POST /search`: Execute hybrid dense vector + sparse keyword search with explainability rationale.

### 8. Approval Center (`/api/v1/approvals`)
- `GET /`: List pending human-in-the-loop authorizations.
- `POST /{id}/action`: Execute approval action (`APPROVE`, `REJECT`, `EDIT`).

### 9. Academic Demonstration Mode (`/api/v1/academic-demo`)
- `POST /pipeline-step`: Run any of the 14 individual algorithms in isolation for project viva presentation.
