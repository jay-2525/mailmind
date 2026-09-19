# InboxGuard Chrome Extension (Manifest V3)

> **Agentic AI for Smart Email and Career Intelligence directly inside your browser and Gmail.**

The **InboxGuard Chrome Extension** brings MailMind's backend intelligence into your daily email workflow:
1. **Gmail Floating Pill**: Directly injects an AI intelligence assistant into `https://mail.google.com`.
2. **Instant Status & Insights**: Shows recoverable storage, pending approvals, urgent emails, and verified career matches.
3. **One-Click Dashboard Access**: Open the full InboxGuard Dashboard or trigger on-demand sync from anywhere.
4. **Active Badge Notifications**: Alerts you with a red badge when high-risk actions require authorization in the Human-in-the-Loop Approval Center.

---

## 🚀 How to Install in Google Chrome (Step-by-Step)

### Option 1: Load Unpacked (Development / Local Installation)
1. Open Google Chrome.
2. Navigate to `chrome://extensions/` in the address bar (or go to **Settings** > **Extensions**).
3. In the top-right corner, turn **ON** the **Developer mode** toggle.
4. Click the **"Load unpacked"** button in the top-left corner.
5. In the file picker, select this directory:
   ```
   C:\Users\ajayb\.gemini\antigravity\scratch\inboxguard\extension
   ```
   *(or the `extension/` folder inside your cloned repo)*.
6. The **InboxGuard** extension icon will now appear in your Chrome toolbar and extensions list!

### Option 2: Install from Pre-Packaged ZIP
1. Download `inboxguard-chrome-extension.zip` from the project root or GitHub releases.
2. Unzip it into any folder (e.g., `C:\InboxGuard-Extension`).
3. Follow the steps in Option 1 and point to the unzipped folder.

---

## ⚙️ Prerequisites
The Chrome extension interacts with the local InboxGuard backend:
1. Ensure the InboxGuard backend is running:
   ```cmd
   start_inboxguard.bat
   ```
   *(Backend will be active at `http://localhost:8000`, Dashboard at `http://localhost:5173`)*.
2. If the backend is not running, the extension displays a friendly offline standby message.

---

## 🧩 Features & Structure

- `manifest.json`: Manifest V3 specification with permissions for Gmail (`https://mail.google.com/*`) and local API (`http://localhost:8000/*`).
- `background/service_worker.js`: Background event worker that polls pending approvals every 5 minutes and updates the extension icon badge counter.
- `content/content.js` & `content/content.css`: Injects an elegant, non-intrusive floating intelligence pill in the bottom-right corner of Gmail. Clicking it opens a live summary drawer.
- `popup/popup.html`, `popup.css`, `popup.js`: Rich multi-tab popup UI with:
  - Overview KPI metrics (Urgent emails, Storage waste %, Job matches, Recoverable MB)
  - **Urgent Tab**: Priority emails requiring immediate action
  - **Storage Tab**: High-waste messages with recommended actions (Archive/Purge)
  - **Jobs Tab**: High-match career opportunities with Trust and Match scores
  - **Approvals Tab**: Actions held for user consent
