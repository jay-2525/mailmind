# Local Development & Setup Guide: MailMind (InboxGuard)

> Follow these step-by-step instructions to clone, configure, run, and test **MailMind (InboxGuard)** on your local development machine.

---

## 1. Prerequisites

Ensure you have the following installed on your system:
- **Python**: Version `3.10` or higher (Python 3.11 / 3.12 / 3.14 verified)
- **Node.js**: Version `18.0.0` or higher (includes `npm`)
- **Git**: Version `2.30` or higher
- **Web Browser**: Google Chrome (for the Manifest V3 Extension) or any Chromium-based browser (Edge, Brave)

---

## 2. Quick 1-Click Launch (Recommended for Windows)

In the project root directory, we provide convenient launcher scripts:

### Option A: Double-Click Batch Launcher
Double-click `start_inboxguard.bat` in File Explorer. This opens two simultaneous terminal windows:
- **Window 1**: FastAPI Backend at `http://localhost:8000`
- **Window 2**: React Vite Frontend at `http://localhost:5173`

### Option B: PowerShell Launcher
```powershell
.\start_inboxguard.ps1
```

> **Note**: If PowerShell displays an *ExecutionPolicy* restriction, run this once:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> .\start_inboxguard.ps1
> ```

---

## 3. Manual Step-by-Step Installation

### 3.1 Clone the Repository
```bash
git clone https://github.com/jay-2525/mailmind.git
cd mailmind
```

### 3.2 Backend Setup (Python / FastAPI)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```powershell
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   ```powershell
   # Copy sample configuration
   cp ..\.env.example .env
   ```
5. Run database initialization and startup:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
6. Verify backend health:
   - Open: `http://localhost:8000/health` (should return `{"status": "HEALTHY"}`)
   - Interactive Swagger API: `http://localhost:8000/docs`

---

### 3.3 Frontend Setup (React / Vite / TypeScript)
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Access the dashboard:
   - Open your browser to: `http://localhost:5173`

---

## 4. Google Chrome Extension Setup (Manifest V3)

The extension allows you to inspect real personal emails directly inside `https://mail.google.com`:

1. Open **Google Chrome**.
2. In the URL address bar, enter:
   ```text
   chrome://extensions/
   ```
3. In the top-right corner, toggle **Developer mode** to **ON**.
4. In the top-left corner, click **Load unpacked**.
5. Select the `extension/` folder inside the cloned project directory (or unzip `inboxguard-chrome-extension.zip`).
6. Navigate to [https://mail.google.com](https://mail.google.com):
   - You will see the **InboxGuard AI** floating badge appear in the bottom-right corner!
   - Click it to view live storage waste, urgent action items, and career opportunities.
   - Click **"Open Dashboard"** to switch directly to the full analytics view.

---

## 5. Environment Variables Reference (`.env`)

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `APP_ENV` | `demo` | Environment mode (`demo`, `development`, `production`) |
| `DEBUG` | `true` | Enables detailed logging and Swagger docs |
| `PORT` | `8000` | Backend API port |
| `SECRET_KEY` | *(random 64-char key)* | Secret for signing JWT session tokens |
| `DATABASE_URL` | `sqlite:///./inboxguard.db` | Connection string (SQLite or PostgreSQL) |
| `LLM_PROVIDER` | `heuristic` | LLM engine (`heuristic`, `gemini`, `openai`, `ollama`) |
| `GEMINI_API_KEY` | `""` | Optional Google Gemini API key |
| `EMBEDDING_PROVIDER` | `sentence-transformers`| Embedding generator |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Dense sentence transformer model |
| `GOOGLE_CLIENT_ID` | `""` | Optional Google Cloud OAuth Client ID |
| `GOOGLE_CLIENT_SECRET` | `""` | Optional Google Cloud OAuth Client Secret |

---

## 6. Troubleshooting & FAQ

### Issue: Port 8000 or 5173 is already in use
**Solution**:
```powershell
# Check what is using port 8000
Get-NetTCPConnection -LocalPort 8000
# Kill process by PID
Stop-Process -Id <PID> -Force
```

### Issue: Hugging Face rate limit warning on first run
**Explanation**: When downloading `all-MiniLM-L6-v2` (23 MB) on the first start, Hugging Face may log an unauthenticated warning.  
**Solution**: This is a harmless one-time download and caches locally in `~/.cache/huggingface/`. No token is required.

### Issue: Frontend Vite build warning about large chunks
**Explanation**: Rollup minifies code into clean bundles.  
**Solution**: Run `npm run build` — the production build compiles with zero errors into `dist/`.
