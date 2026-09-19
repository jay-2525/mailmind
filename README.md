# MailMind: Agentic AI for Smart Email and Career Intelligence
### Product & Application Name: **InboxGuard**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic%20Orchestration-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![React 18](https://img.shields.io/badge/React-18.3+-61dafb.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Approved Academic Project Title**: *MailMind: Agentic AI for Smart Email and Career Intelligence*  
> **Product / Application Name**: *InboxGuard* (used in the UI, dashboard, branding, and documentation).

---

## 1. Project Overview

**InboxGuard (MailMind)** is an end-to-end, production-style Agentic AI Email Intelligence and Decision Support System that integrates with Gmail and Google Calendar. It is **not** a simple email chatbot or a naive spam classifier. It analyzes email communications using multi-signal decision intelligence:

$$\text{Read} \longrightarrow \text{Understand} \longrightarrow \text{Retrieve Context (RAG)} \longrightarrow \text{Score} \longrightarrow \text{Reason (LangGraph)} \longrightarrow \text{Check Policy} \longrightarrow \text{Human Approval} \longrightarrow \text{Execute \& Audit}$$

### Three Core Capabilities:
1. **Smart Storage Cleanup**: Configurable, explainable **Storage Waste Scoring**, semantic redundancy detection via vector cosine similarity, and human-authorized archiving/deletion.
2. **Personal Task & Commitment Management**: NER-based action item extraction, temporal deadline parsing, and a **Finite State Machine (FSM)** tracking conversational commitments (`OPEN` $\to$ `PROMISED` $\to$ `COMPLETED` / `OVERDUE`).
3. **Career & Job Opportunity Intelligence**: Recruitment email detection, recruiter domain legitimacy & trust scoring, resume parsing, mathematical **Job Match Scoring** (Required Skills + Preferred Skills + Experience + Education + Semantic Cosine Similarity), and application preparation (tailored cover letters, recruiter pitches, interview Q&A).
4. **Google Chrome Extension (Manifest V3)**: Injects an AI intelligence badge into Gmail (`https://mail.google.com`), provides a multi-tab quick popup for storage waste, pending approvals, urgent follow-ups, and career matches, and notifies you when actions require authorization. Anyone can download and install it in seconds!
5. **Untrusted Input Treatment & Safety Policy Guard**: Every email body is treated strictly as untrusted input. Malicious prompt-injection attempts are quarantined and neutralized. Destructive and external actions require explicit human authorization in the **Approval Center**.
6. **Academic Demonstration & Viva Mode**: A dedicated interactive dashboard showcasing all 14 algorithmic steps with live interactive inputs, formulas, intermediate vector calculations, and outputs for your final-year B.Tech CSE project defense.

---

## 🌐 Chrome Extension (Download & Install in 60s)

InboxGuard includes a full Google Chrome Extension that integrates directly with your personal email in Gmail!

### Instant Installation:
1. **Download the Extension**: Grab [`inboxguard-chrome-extension.zip`](inboxguard-chrome-extension.zip) directly from this repository (or use the [`extension/`](extension/) directory).
2. **Open Chrome Extensions**: In your Chrome address bar, open:
   ```
   chrome://extensions/
   ```
3. **Enable Developer Mode**: Turn ON the toggle in the top-right corner.
4. **Load Extension**: Click **Load unpacked** (top-left) and select either:
   - The unzipped folder of `inboxguard-chrome-extension.zip`, OR
   - The `extension/` folder inside your cloned repository.
5. **Open Gmail**: Visit `https://mail.google.com` to see the **InboxGuard AI** floating pill appear in the bottom-right corner!

---

## 🐙 How to Host this Project on GitHub

This repository is completely prepared with clean git history, safe `.gitignore` (protecting your database, credentials, and dependencies), and pre-built distribution assets.

Follow these 3 steps to publish it to your GitHub account:

### Step 1: Create a New Repository on GitHub
1. Go to [github.com/new](https://github.com/new).
2. Name your repository (e.g., `inboxguard` or `mailmind-email-intelligence`).
3. Set the visibility to **Public** or **Private** (do **NOT** check "Initialize with README", as this repo already has a comprehensive README).
4. Click **Create repository**.

### Step 2: Push to GitHub from your Terminal
Open PowerShell or Command Prompt inside this project folder:

```powershell
# 1. Set the main branch
git branch -M main

# 2. Add your GitHub repository as the remote origin
git remote add origin https://github.com/<YOUR-GITHUB-USERNAME>/inboxguard.git

# 3. Push all code and assets
git push -u origin main
```

*(Replace `<YOUR-GITHUB-USERNAME>` with your actual GitHub username).*

---

---

## 2. High-Level Architecture

```mermaid
flowchart TD
    Gmail[Gmail API / Ingestion] --> Thread[Threading & Normalization]
    Thread --> NLP[NLP & Entity Extractor (NER + Time)]
    NLP --> Embed[Embedding Service (all-MiniLM-L6-v2)]
    Embed --> RAG[Hybrid RAG Engine (Vector + BM25 RRF)]
    
    subgraph Multi-Signal Analysis
        Embed --> Storage[Storage Waste Scorer]
        Embed --> TaskFSM[Task & Commitment FSM]
        Embed --> JobIntel[Job Intelligence & Trust Scorer]
    end
    
    Storage --> LangGraph[LangGraph Agent Orchestrator]
    TaskFSM --> LangGraph
    JobIntel --> LangGraph
    RAG --> LangGraph
    
    LangGraph --> Decision[Decision Agent: Action & Confidence]
    Decision --> Guard[Safety & Policy Guard]
    Guard --> HITL{Risk Tier?}
    HITL -- Low Risk --> AutoExec[Safe Auto-Log / Classify]
    HITL -- Med / High Risk --> ApprovalQueue[Approval Center]
    ApprovalQueue --> UserUI[User Approval / Reject / Edit]
    UserUI -- Approved --> Exec[Action Execution Service]
    Exec --> GAction[Gmail Trash / Archive]
    Exec --> CalAction[Google Calendar API]
    Exec --> Audit[(Audit Log Trail)]
```

---

## 3. Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React, Recharts analytics, React Router.
- **Backend**: Python, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, SQLite (out-of-the-box local demo) / PostgreSQL 16 with `pgvector` (production Docker).
- **AI / Agentic Layer**: LangGraph state machine orchestrator, Sentence Transformers (`all-MiniLM-L6-v2`), scikit-learn cosine similarity, lexical NER and temporal parsers, LLM provider abstraction (Google Gemini, OpenAI, Ollama, and Heuristic offline NLP engine).
- **Integrations**: Gmail API, Google Calendar API, Google OAuth 2.0 with least-privilege scopes.
- **Testing**: Pytest, FastAPI TestClient, unit tests, end-to-end integration tests.

---

## 4. Quickstart Guide (Local Development)

### Prerequisites
- Python 3.10+
- Node.js 18+

### Step 1: Start the Backend
```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- The backend automatically initializes the database tables (`inboxguard.db`), loads the `all-MiniLM-L6-v2` embedding model, and seeds 10 realistic demo emails.
- Swagger API Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Step 2: Start the Frontend
```powershell
cd frontend
npm run dev
```
- Open your browser to `http://localhost:5173`.
- The dashboard will load with full executive KPIs, urgent action items, storage waste metrics, and top job matches.

---

## 5. Running with Docker Compose (PostgreSQL + pgvector)

```powershell
docker-compose up --build -d
```
Spins up:
- `inboxguard_postgres`: PostgreSQL with pgvector extension enabled on port 5432
- `inboxguard_backend`: FastAPI on port 8000
- `inboxguard_frontend`: Production Nginx container on port 5173

---

## 6. Running Automated Tests

Run the complete 12-test suite covering scoring formulas, commitment FSM, redundancy detection, safety policy guard, prompt injection defense, and the full end-to-end pipeline:

```powershell
cd backend
python -m pytest tests -v
```

Expected output:
```
============================= 12 passed in 25s =============================
```

---

## 7. Project Folder Structure

```
inboxguard/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # 13 REST API route controllers
│   │   ├── core/            # Config, database session, security utils
│   │   ├── models/          # 18 SQLAlchemy domain models
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── services/        # Embedding, LLM provider, NLP & FSM engines
│   │   ├── agents/          # LangGraph state machine orchestrator
│   │   ├── rag/             # Hybrid RAG (Vector + BM25 RRF)
│   │   ├── scoring/         # Storage Waste, Redundancy, Job Match, Trust
│   │   ├── safety/          # Policy guard & prompt-injection defense
│   │   ├── integrations/    # Gmail API, Calendar API, Google OAuth
│   │   ├── demo/            # Seed dataset generator (10 realistic emails)
│   │   └── main.py          # FastAPI application entrypoint
│   ├── tests/               # 12 automated unit & integration tests
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/      # Navbar, Sidebar, NavView
│   │   ├── pages/           # 12 full dashboard views
│   │   ├── services/api.ts  # Centralized REST client
│   │   ├── types/           # TypeScript domain definitions
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
│
├── docs/                    # Complete architectural documentation & formulas
│   ├── architecture.md
│   ├── database.md
│   ├── ai-pipeline.md
│   ├── rag.md
│   ├── scoring.md
│   ├── safety.md
│   ├── api.md
│   ├── setup.md
│   └── testing.md
│
├── extension/               # Google Chrome Extension (Manifest V3)
│   ├── manifest.json        # Extension configuration
│   ├── background/          # Background service worker (alerts)
│   ├── content/             # Injected Gmail floating widget
│   ├── popup/               # Multi-tab interactive popup dashboard
│   └── icons/               # Extension icons
│
├── inboxguard-chrome-extension.zip  # Downloadable standalone extension archive
├── scripts/                 # Automation & packaging scripts
├── start_inboxguard.bat     # One-click Windows launcher (Backend + Frontend)
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 8. Academic Viva & Review Features

To demonstrate the algorithmic depth during your project viva/review:
1. Navigate to the **Academic Viva Mode** tab in the sidebar.
2. Interactively test all 10 core algorithms:
   - **Storage Waste Score**: Inspect the exact penalty points (+25 for promo, +20 for duplicate, -20 for active task).
   - **Job Match Scoring**: Inspect required vs preferred skill overlap and 384d cosine similarity.
   - **Semantic Duplicate Detection**: View normalized subject matching and cosine vector distance.
   - **Recruiter Trust Scorer**: Test advance-fee check scam patterns and domain consistency.
   - **Commitment FSM**: Verify state transitions (`OPEN` $\to$ `PROMISED` $\to$ `COMPLETED` / `OVERDUE`).
   - **Hybrid RAG**: View why historical emails were retrieved with explainability notes.
   - **Safety Policy Guard**: Test adversarial prompt injection inputs.
   - **LangGraph Agent**: Trace all 7 nodes from email understanding to approval routing.

---

## 9. Security & Responsible AI Principles

- **No Silent Destructive Actions**: Deletion or mailbox emptying requires explicit confirmation in the Approval Center.
- **Untrusted Input Boundary**: Email text is quarantined and never allowed to manipulate system directives.
- **Explainability**: Every score displays its itemized contribution factors ("Why?").
- **Auditability**: Every decision and user authorization is logged to the immutable `audit_logs` table.

---

## 10. License

This project is licensed under the MIT License - see the LICENSE file for details.
