# Setup & Installation Guide: MailMind (InboxGuard)

## Quickstart Prerequisites
- Python 3.10+ (Tested on Python 3.14 / 3.11)
- Node.js 18+ (Tested on Node.js 20 LTS)
- Git

---

## 1. Local Development (Instant Zero-Setup Mode)

InboxGuard supports a self-contained local mode using SQLite and local SentenceTransformers embeddings without requiring Docker or external services.

### Backend Setup
```powershell
cd backend

# Create or use environment
pip install -r requirements.txt

# Run backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will automatically:
1. Create SQLite tables (`inboxguard.db`).
2. Load SentenceTransformer embeddings (`all-MiniLM-L6-v2`).
3. Seed 10 realistic demo emails, candidate resume, and jobs.
4. Start REST API at `http://localhost:8000` (Docs at `http://localhost:8000/docs`).

---

### Frontend Setup
```powershell
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

Frontend runs at `http://localhost:5173`.

---

## 2. Production Docker Deployment (PostgreSQL + pgvector)

```powershell
# In the root project directory
docker-compose up --build -d
```

This spins up:
- `inboxguard_postgres`: PostgreSQL 16 with `pgvector`
- `inboxguard_backend`: FastAPI production container
- `inboxguard_frontend`: Nginx production frontend container

---

## 3. Google Workspace OAuth Setup (Optional)

To connect live Gmail and Google Calendar APIs:
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create an OAuth 2.0 Client ID (Web Application).
3. Set Authorized Redirect URI: `http://localhost:8000/api/v1/auth/google/callback`.
4. Enable **Gmail API** and **Google Calendar API**.
5. Add credentials to `.env`:
   ```env
   GOOGLE_CLIENT_ID=your_client_id_here
   GOOGLE_CLIENT_SECRET=your_client_secret_here
   ```
