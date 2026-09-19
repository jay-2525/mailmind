// InboxGuard Gmail Content Script
// Inspects personal emails in Gmail dynamically for ANY logged-in user and synchronizes them directly with the InboxGuard AI backend

(function () {
  'use strict';

  if (document.getElementById('inboxguard-gmail-root')) return;

  const BACKEND_URL = 'http://localhost:8000/api/v1';
  const DASHBOARD_URL = 'http://localhost:5173';

  // Active user state
  let activeUser = {
    email: '',
    name: 'Gmail'
  };

  let currentToken = null;

  // Helper to format clean display name
  function formatDisplayName(rawName, email) {
    if (rawName && rawName.trim()) {
      let cleaned = rawName.replace(/^Google Account:\s*/i, '').trim();
      cleaned = cleaned.replace(/\s*\([^)]+@[^)]+\)\s*/g, '').trim();
      if (cleaned.length > 1 && !cleaned.includes('@')) {
        return cleaned;
      }
    }
    if (email && email.includes('@')) {
      const part = email.split('@')[0].replace(/[._+-]+/g, ' ');
      return part.charAt(0).toUpperCase() + part.slice(1);
    }
    return 'Gmail';
  }

  // 1. Multi-strategy dynamic Gmail user detection for ANY account
  function detectGmailUser() {
    const emailRegex = /([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/;

    // Strategy A: Check Google Account header buttons (e.g. "Google Account: Name (email@domain.com)")
    const headerSelectors = [
      'a[aria-label*="Google Account:"]',
      'button[aria-label*="Google Account:"]',
      'a[aria-label*="Google Account"]',
      'button[aria-label*="Google Account"]',
      'a[href*="SignOutOptions"]',
      'a[href*="accounts.google.com"]',
      'header a[aria-label*="@"]',
      '[data-email]',
      '.gb_A[aria-label]',
      'a.gb_d[aria-label]',
      '.gb_d[aria-label]'
    ];

    for (const sel of headerSelectors) {
      const el = document.querySelector(sel);
      if (el) {
        const label = el.getAttribute('aria-label') || el.getAttribute('data-email') || el.getAttribute('title') || '';
        const match = label.match(emailRegex);
        if (match && match[1]) {
          const email = match[1].trim().toLowerCase();
          const nameMatch = label.match(/Google Account:\s*([^(]+?)(?:\s*\(|\s*$)/i);
          const name = formatDisplayName(nameMatch ? nameMatch[1] : '', email);
          return { email, name };
        }
      }
    }

    // Strategy B: Check document title (e.g. "Inbox (15) - user@domain.com - Gmail")
    const titleMatch = document.title.match(emailRegex);
    if (titleMatch && titleMatch[1]) {
      const email = titleMatch[1].trim().toLowerCase();
      return { email, name: formatDisplayName('', email) };
    }

    // Strategy C: Check account switcher / hovercards / user avatars
    const hoverEl = document.querySelector('[data-hovercard-id*="@"], img[alt*="@"]');
    if (hoverEl) {
      const val = hoverEl.getAttribute('data-hovercard-id') || hoverEl.getAttribute('alt') || '';
      const match = val.match(emailRegex);
      if (match && match[1]) {
        const email = match[1].trim().toLowerCase();
        return { email, name: formatDisplayName('', email) };
      }
    }

    // Strategy D: Check URL for /u/user@domain.com or user parameter
    const urlMatch = window.location.href.match(/\/mail\/u\/([^/?#]+@[^/?#]+)/);
    if (urlMatch && urlMatch[1]) {
      const email = decodeURIComponent(urlMatch[1]).trim().toLowerCase();
      return { email, name: formatDisplayName('', email) };
    }

    // Strategy E: Keep existing valid user if already identified
    if (activeUser.email) {
      return activeUser;
    }

    return { email: '', name: 'Gmail' };
  }

  // 2. Extract emails currently visible in the Gmail Inbox table dynamically
  function extractEmailsFromGmailDOM() {
    const extracted = [];
    const seen = new Set();
    const rows = document.querySelectorAll('tr.zA, tr[role="row"], div[role="row"], .Cp tr');

    rows.forEach((row, idx) => {
      try {
        const senderEl = row.querySelector('span.bA4 span, span.zF, span.yP, [email], .yW span, [data-hovercard-id], .yX span, .bA4');
        const sender = senderEl ? (senderEl.getAttribute('email') || senderEl.textContent.trim()) : 'Unknown Sender';

        const subjectEl = row.querySelector('span.bqe, .bog span, span[data-thread-id], .y6 span, span.bog');
        const subject = subjectEl ? subjectEl.textContent.trim() : '';

        const snippetEl = row.querySelector('span.y2, .y2');
        let body = snippetEl ? snippetEl.textContent.trim() : '';
        body = body.replace(/^[-–—]\s*/, '');

        const dateEl = row.querySelector('td.xW span, span.xW, td.bq4, .bq4, time');
        const dateStr = dateEl ? dateEl.textContent.trim() : '';

        const isUnread = row.classList.contains('zE') || row.querySelector('.zE') !== null;
        const rowId = row.getAttribute('data-legacy-thread-id') || row.id || `gmail_item_${idx}`;

        // Deduplicate rows
        const dedupeKey = `${subject}__${dateStr}__${sender}`;
        if (subject && !seen.has(dedupeKey)) {
          seen.add(dedupeKey);
          extracted.push({
            id: rowId,
            sender: sender || 'Sender',
            subject: subject,
            body_preview: body || subject,
            date_str: dateStr,
            is_unread: isUnread
          });
        }
      } catch (e) {
        // Skip malformed row
      }
    });

    return extracted;
  }

  // 3. Construct and Mount Widget
  const root = document.createElement('div');
  root.id = 'inboxguard-gmail-root';

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
          <span class="inboxguard-drawer-title">InboxGuard AI Assistant</span>
        </div>
        <button id="inboxguard-close-btn" style="background:none; border:none; color:#94a3b8; cursor:pointer; font-size:16px;">✕</button>
      </div>

      <!-- User Info Badge -->
      <div class="inboxguard-user-badge" id="inboxguard-user-badge">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        <div style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex:1;">
          <span id="ig-user-name" style="font-weight:700; color:#e2e8f0;">Loading...</span>
          <span id="ig-user-email" style="color:#94a3b8; margin-left:4px; font-size:10px;">(detecting account...)</span>
        </div>
        <button id="ig-edit-user-btn" style="background:none; border:none; color:#818cf8; cursor:pointer; font-size:12px; padding:0 4px;" title="Change / Set email manually">✎</button>
      </div>

      <div id="inboxguard-body-content">
        <!-- Sync Action Button -->
        <button id="inboxguard-sync-btn" class="inboxguard-btn-sync">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
          <span id="inboxguard-sync-text">⚡ Sync Gmail to Dashboard</span>
        </button>

        <div style="display:flex; flex-direction:column; gap:8px; margin-top:8px;">
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

        <div id="ig-notice-box" style="margin-top:8px; padding:8px; background:rgba(30, 41, 59, 0.7); border-radius:8px; font-size:11px; color:#cbd5e1; border-left:3px solid #6366f1;">
          Click Sync to analyze personal Gmail emails with local AI Agent.
        </div>

        <div style="display:flex; gap:8px; margin-top:10px;">
          <a id="ig-open-dash-btn" href="${DASHBOARD_URL}" target="_blank" class="inboxguard-btn" style="flex:1;">
            Open Dashboard ↗
          </a>
          <button id="ig-refresh-btn" class="inboxguard-btn" style="background:#334155; cursor:pointer;" title="Refresh metrics">
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
  const syncBtn = document.getElementById('inboxguard-sync-btn');
  const syncText = document.getElementById('inboxguard-sync-text');
  const openDashBtn = document.getElementById('ig-open-dash-btn');
  const editUserBtn = document.getElementById('ig-edit-user-btn');

  // Update User UI Elements
  function updateUserUI() {
    const nameEl = document.getElementById('ig-user-name');
    const emailEl = document.getElementById('ig-user-email');

    if (nameEl) nameEl.textContent = activeUser.name || 'Gmail';
    if (emailEl) emailEl.textContent = activeUser.email ? `(${activeUser.email})` : '(detecting account...)';

    if (syncText && !syncBtn.disabled) {
      syncText.textContent = activeUser.name && activeUser.name !== 'Gmail'
        ? `⚡ Sync ${activeUser.name}'s Gmail to Dashboard`
        : '⚡ Sync Gmail to Dashboard';
    }
  }

  // Refresh user detection
  function refreshUserDetection() {
    const detected = detectGmailUser();
    if (detected.email) {
      activeUser = detected;
      updateUserUI();
    }
  }

  // Load cached user email if available
  if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
    chrome.storage.local.get(['inboxguard_token', 'user_email'], (res) => {
      if (res.inboxguard_token) {
        currentToken = res.inboxguard_token;
        openDashBtn.href = `${DASHBOARD_URL}?token=${currentToken}`;
      }
      if (res.user_email) {
        activeUser.email = res.user_email;
        activeUser.name = formatDisplayName('', res.user_email);
        updateUserUI();
      }
      refreshUserDetection();
    });
  } else {
    refreshUserDetection();
  }

  // Allow manual email entry / override
  if (editUserBtn) {
    editUserBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const entered = prompt('Enter your Gmail address for InboxGuard intelligence:', activeUser.email || '');
      if (entered && entered.includes('@')) {
        const cleanEmail = entered.trim().toLowerCase();
        activeUser = {
          email: cleanEmail,
          name: formatDisplayName('', cleanEmail)
        };
        updateUserUI();
        if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
          chrome.storage.local.set({ user_email: activeUser.email });
        }
      }
    });
  }

  toggleBtn.addEventListener('click', () => {
    refreshUserDetection();
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
    refreshUserDetection();
    fetchSummary();
  });

  syncBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    triggerSync();
  });

  // 4. Synchronize Gmail emails with InboxGuard backend
  async function triggerSync() {
    refreshUserDetection();

    const noticeBox = document.getElementById('ig-notice-box');

    // If still no email detected, prompt user
    if (!activeUser.email) {
      const entered = prompt('Please enter your Gmail address to connect to InboxGuard:', '');
      if (entered && entered.includes('@')) {
        const cleanEmail = entered.trim().toLowerCase();
        activeUser = {
          email: cleanEmail,
          name: formatDisplayName('', cleanEmail)
        };
        updateUserUI();
      } else {
        if (noticeBox) {
          noticeBox.innerHTML = '⚠️ <strong>Email required:</strong> Please click ✎ above to enter your Gmail address.';
          noticeBox.style.borderLeftColor = '#ef4444';
        }
        return;
      }
    }

    const emails = extractEmailsFromGmailDOM();
    if (emails.length === 0) {
      if (noticeBox) {
        noticeBox.innerHTML = '⚠️ <strong>No visible emails found:</strong> Please open your Gmail Inbox or wait for emails to finish loading.';
        noticeBox.style.borderLeftColor = '#f59e0b';
      }
      syncText.textContent = '⚠️ No Emails Found in View';
      setTimeout(() => {
        updateUserUI();
      }, 3000);
      return;
    }

    syncBtn.disabled = true;
    syncText.textContent = '🔄 Syncing with local AI Agent...';

    try {
      const res = await fetch(`${BACKEND_URL}/emails/sync-from-extension`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_email: activeUser.email,
          user_name: activeUser.name,
          emails: emails
        })
      });

      if (!res.ok) throw new Error('Sync failed');
      const data = await res.json();

      currentToken = data.access_token;
      if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
        chrome.storage.local.set({
          inboxguard_token: data.access_token,
          user_email: activeUser.email
        });
      }

      // Update Dashboard Link with Token so clicking it immediately opens as this user
      openDashBtn.href = `${DASHBOARD_URL}?token=${currentToken}`;

      syncText.textContent = `✓ ${emails.length} Emails Synced!`;
      syncBtn.style.background = '#10b981';

      setTimeout(() => {
        syncText.textContent = activeUser.name && activeUser.name !== 'Gmail'
          ? `⚡ Re-Sync ${activeUser.name}'s Gmail`
          : '⚡ Re-Sync Gmail';
        syncBtn.disabled = false;
        syncBtn.style.background = '';
      }, 3000);

      // Refresh KPIs
      await fetchSummary();

    } catch (err) {
      console.error('[InboxGuard Content Script] Sync error:', err);
      syncText.textContent = '❌ Sync Failed (Check Backend)';
      syncBtn.style.background = '#ef4444';
      setTimeout(() => {
        updateUserUI();
        syncBtn.disabled = false;
        syncBtn.style.background = '';
      }, 3000);
    }
  }

  // 5. Fetch live intelligence summary
  async function fetchSummary() {
    const statusDot = document.getElementById('inboxguard-status-dot');
    const noticeBox = document.getElementById('ig-notice-box');
    const badge = document.getElementById('inboxguard-badge');

    const headers = {};
    if (currentToken) {
      headers['Authorization'] = `Bearer ${currentToken}`;
    }

    try {
      const res = await fetch(`${BACKEND_URL}/dashboard/summary`, { headers });
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
        noticeBox.innerHTML = `🛡️ Mailbox guarded. ${data.kpis.recoverable_mb || 0} MB recoverable space ready for cleanup.`;
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

  // 6. Observe document title and DOM changes to detect email when Gmail finishes loading
  const observer = new MutationObserver(() => {
    if (!activeUser.email) {
      refreshUserDetection();
    }
  });

  observer.observe(document.head || document.documentElement, {
    childList: true,
    subtree: true,
    characterData: true
  });

  // Re-detect on window load and after 2.5 seconds
  window.addEventListener('load', refreshUserDetection);
  setTimeout(refreshUserDetection, 2500);

})();
