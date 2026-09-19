// InboxGuard Gmail Content Script
// Injects an AI Intelligence Floating Assistant directly into Gmail

(function () {
  'use strict';

  // Prevent multiple injections
  if (document.getElementById('inboxguard-gmail-root')) return;

  const BACKEND_URL = 'http://localhost:8000/api/v1';
  const DASHBOARD_URL = 'http://localhost:5173';

  // Create root container
  const root = document.createElement('div');
  root.id = 'inboxguard-gmail-root';

  // Build Floating Pill + Drawer HTML
  root.innerHTML = `
    <div class="inboxguard-floating-pill" id="inboxguard-toggle" title="Click to view InboxGuard Intelligence">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      </svg>
      <span>InboxGuard AI</span>
      <span id="inboxguard-badge" style="display:none; background:#ef4444; color:#fff; font-size:10px; padding:1px 5px; border-radius:9999px; font-weight:700;">0</span>
    </div>

    <div class="inboxguard-drawer" id="inboxguard-drawer">
      <div class="inboxguard-drawer-header">
        <div style="display:flex; align-items:center; gap:6px;">
          <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#10b981;" id="inboxguard-status-dot"></span>
          <span class="inboxguard-drawer-title">MailMind / InboxGuard AI</span>
        </div>
        <button id="inboxguard-close-btn" style="background:none; border:none; color:#94a3b8; cursor:pointer; font-size:16px;">✕</button>
      </div>

      <div id="inboxguard-body-content">
        <div style="font-size:11px; color:#94a3b8; line-height:1.4;">
          Personal Email & Career Intelligence Agent active.
        </div>

        <div style="display:flex; flex-direction:column; gap:8px; margin-top:4px;">
          <div class="inboxguard-stat-row">
            <span>Storage Waste Detected</span>
            <span class="inboxguard-stat-val" id="ig-waste-val" style="color:#f87171;">--</span>
          </div>
          <div class="inboxguard-stat-row">
            <span>Recoverable Space</span>
            <span class="inboxguard-stat-val" id="ig-storage-val" style="color:#fbbf24;">--</span>
          </div>
          <div class="inboxguard-stat-row">
            <span>Urgent Follow-ups</span>
            <span class="inboxguard-stat-val" id="ig-urgent-val" style="color:#818cf8;">--</span>
          </div>
          <div class="inboxguard-stat-row">
            <span>Career Opportunities</span>
            <span class="inboxguard-stat-val" id="ig-jobs-val" style="color:#34d399;">--</span>
          </div>
          <div class="inboxguard-stat-row">
            <span>Pending Approvals</span>
            <span class="inboxguard-stat-val" id="ig-approvals-val" style="color:#ec4899;">--</span>
          </div>
        </div>

        <div id="ig-notice-box" style="margin-top:4px; padding:8px; background:rgba(30, 41, 59, 0.7); border-radius:8px; font-size:11px; color:#cbd5e1; border-left:3px solid #6366f1;">
          Loading local agent intelligence...
        </div>

        <div style="display:flex; gap:8px; margin-top:8px;">
          <a href="${DASHBOARD_URL}" target="_blank" class="inboxguard-btn" style="flex:1;">
            Open Dashboard ↗
          </a>
          <button id="ig-refresh-btn" class="inboxguard-btn" style="background:#334155; cursor:pointer;" title="Refresh intelligence">
            ↻
          </button>
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(root);

  const toggleBtn = document.getElementById('inboxguard-toggle');
  const drawer = document.getElementById('inboxguard-drawer');
  const closeBtn = document.getElementById('inboxguard-close-btn');
  const refreshBtn = document.getElementById('ig-refresh-btn');

  toggleBtn.addEventListener('click', () => {
    drawer.classList.toggle('open');
    if (drawer.classList.contains('open')) {
      fetchSummary();
    }
  });

  closeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    drawer.classList.remove('open');
  });

  refreshBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fetchSummary();
  });

  async function fetchSummary() {
    const statusDot = document.getElementById('inboxguard-status-dot');
    const noticeBox = document.getElementById('ig-notice-box');
    const badge = document.getElementById('inboxguard-badge');

    try {
      const res = await fetch(`${BACKEND_URL}/dashboard/summary`);
      if (!res.ok) throw new Error('API offline');
      const data = await res.json();

      statusDot.style.background = '#10b981';
      document.getElementById('ig-waste-val').textContent = `${data.kpis.average_waste_score || 0}%`;
      document.getElementById('ig-storage-val').textContent = `${data.kpis.recoverable_mb || 0} MB`;
      document.getElementById('ig-urgent-val').textContent = `${data.kpis.unread_important || 0}`;
      document.getElementById('ig-jobs-val').textContent = `${data.kpis.high_match_jobs || 0} matches`;
      document.getElementById('ig-approvals-val').textContent = `${data.kpis.pending_approvals || 0} actions`;

      const totalAlerts = (data.kpis.pending_approvals || 0) + (data.kpis.unread_important || 0);
      if (totalAlerts > 0) {
        badge.textContent = totalAlerts;
        badge.style.display = 'inline-block';
      } else {
        badge.style.display = 'none';
      }

      if (data.kpis.pending_approvals > 0) {
        noticeBox.innerHTML = `⚠️ <strong>${data.kpis.pending_approvals} High-Risk actions</strong> require authorization in Approval Center.`;
        noticeBox.style.borderLeftColor = '#ef4444';
      } else if (data.kpis.high_match_jobs > 0) {
        const topJob = (data.top_jobs && data.top_jobs[0]) ? data.top_jobs[0].role : 'high-match roles';
        noticeBox.innerHTML = `🎯 <strong>Career Match:</strong> Identified ${topJob} (${data.kpis.high_match_jobs} suitable matches).`;
        noticeBox.style.borderLeftColor = '#10b981';
      } else {
        noticeBox.innerHTML = `🛡️ Mailbox guarded. ${data.kpis.recoverable_mb || 0} MB recoverable storage ready for cleanup.`;
        noticeBox.style.borderLeftColor = '#6366f1';
      }

    } catch (err) {
      statusDot.style.background = '#ef4444';
      badge.style.display = 'none';
      document.getElementById('ig-waste-val').textContent = 'N/A';
      document.getElementById('ig-storage-val').textContent = 'N/A';
      document.getElementById('ig-urgent-val').textContent = 'N/A';
      document.getElementById('ig-jobs-val').textContent = 'N/A';
      document.getElementById('ig-approvals-val').textContent = 'N/A';
      noticeBox.innerHTML = `🔌 <strong>Local Agent Standby:</strong> Run <code>start_inboxguard.bat</code> to connect local AI intelligence.`;
      noticeBox.style.borderLeftColor = '#f59e0b';
    }
  }

  // Initial check in background after 2 seconds
  setTimeout(fetchSummary, 2000);
})();
