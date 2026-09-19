const BACKEND_URL = 'http://localhost:8000/api/v1';
const DASHBOARD_URL = 'http://localhost:5173';

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initActions();
  fetchIntelligence();
});

function initTabs() {
  const tabs = document.querySelectorAll('.tab-btn');
  const cards = document.querySelectorAll('.kpi-card');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      switchTab(tab.dataset.tab);
    });
  });

  cards.forEach(card => {
    card.addEventListener('click', () => {
      switchTab(card.dataset.tab);
    });
  });
}

function switchTab(tabId) {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabId);
  });
  document.querySelectorAll('.tab-panel').forEach(panel => {
    panel.classList.toggle('active', panel.id === `panel-${tabId}`);
  });
}

async function getAuthHeaders() {
  return new Promise(resolve => {
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
      chrome.storage.local.get(['inboxguard_token', 'user_email'], res => {
        const headers = { 'Content-Type': 'application/json' };
        if (res.inboxguard_token) {
          headers['Authorization'] = `Bearer ${res.inboxguard_token}`;
        }
        resolve(headers);
      });
    } else {
      resolve({ 'Content-Type': 'application/json' });
    }
  });
}

function initActions() {
  document.getElementById('btn-open-dashboard').addEventListener('click', () => {
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
      chrome.storage.local.get('inboxguard_token', res => {
        const url = res.inboxguard_token ? `${DASHBOARD_URL}?token=${res.inboxguard_token}` : DASHBOARD_URL;
        chrome.tabs.create({ url });
      });
    } else {
      chrome.tabs.create({ url: DASHBOARD_URL });
    }
  });

  document.getElementById('btn-sync').addEventListener('click', async () => {
    const btn = document.getElementById('btn-sync');
    btn.style.opacity = '0.5';
    try {
      const headers = await getAuthHeaders();
      await fetch(`${BACKEND_URL}/emails/sync`, { method: 'POST', headers });
      await fetchIntelligence();
    } catch (e) {
      console.error(e);
    } finally {
      btn.style.opacity = '1';
    }
  });

  document.getElementById('btn-quick-archive').addEventListener('click', () => {
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
      chrome.storage.local.get('inboxguard_token', res => {
        const url = res.inboxguard_token ? `${DASHBOARD_URL}?token=${res.inboxguard_token}#storage` : `${DASHBOARD_URL}#storage`;
        chrome.tabs.create({ url });
      });
    } else {
      chrome.tabs.create({ url: `${DASHBOARD_URL}#storage` });
    }
  });
}

async function fetchIntelligence() {
  const statusBadge = document.getElementById('status-text');

  try {
    const headers = await getAuthHeaders();
    const res = await fetch(`${BACKEND_URL}/dashboard/summary`, { headers });
    if (!res.ok) throw new Error('API unreachable');
    const data = await res.json();

    // Check current user profile
    try {
      const userRes = await fetch(`${BACKEND_URL}/auth/me`, { headers });
      if (userRes.ok) {
        const user = await userRes.json();
        statusBadge.textContent = user.is_demo ? 'Demo Mode (Alex)' : `${user.email}`;
      } else {
        statusBadge.textContent = 'Agent Connected';
      }
    } catch (_) {
      statusBadge.textContent = 'Agent Connected';
    }
    statusBadge.parentElement.style.color = '#34d399';

    // Update KPIs
    document.getElementById('kpi-urgent').textContent = data.kpis.unread_important ?? 0;
    document.getElementById('kpi-waste').textContent = `${data.kpis.average_waste_score ?? 0}%`;
    document.getElementById('kpi-jobs').textContent = data.kpis.high_match_jobs ?? 0;
    document.getElementById('kpi-approvals').textContent = data.kpis.pending_approvals ?? 0;
    document.getElementById('storage-recoverable').textContent = `${data.kpis.recoverable_mb ?? 0} MB`;

    // Populate Urgent Tab
    renderUrgentList(data.recent_urgent || []);

    // Populate Jobs Tab
    renderJobsList(data.top_jobs || []);

    // Fetch storage & approvals details
    fetchStorageList();
    fetchApprovalsList();

  } catch (err) {
    statusBadge.textContent = 'Offline (Start Backend)';
    statusBadge.parentElement.style.color = '#f87171';
    document.getElementById('urgent-list').innerHTML = `
      <div class="empty-state">
        <p>InboxGuard Backend is not running.</p>
        <p style="margin-top:6px; font-size:11px; color:#94a3b8;">Run start_inboxguard.bat to activate.</p>
      </div>
    `;
  }
}

function renderUrgentList(items) {
  const container = document.getElementById('urgent-list');
  if (!items || items.length === 0) {
    container.innerHTML = '<div class="empty-state">No urgent emails requiring immediate action.</div>';
    return;
  }

  container.innerHTML = items.map(item => `
    <div class="item-card" onclick="window.open('${DASHBOARD_URL}', '_blank')">
      <div class="item-header">
        <span class="tag tag-rose">${item.category || 'Attention'}</span>
        <span style="color:#fbbf24; font-weight:700;">Urg: ${Math.round((item.urgency || 0.5) * 100)}%</span>
      </div>
      <div class="item-title">${escapeHtml(item.subject)}</div>
      <div class="item-desc">${escapeHtml(item.sender)}</div>
    </div>
  `).join('');
}

function renderJobsList(jobs) {
  const container = document.getElementById('jobs-list');
  if (!jobs || jobs.length === 0) {
    container.innerHTML = '<div class="empty-state">No job opportunities currently identified.</div>';
    return;
  }

  container.innerHTML = jobs.map(job => `
    <div class="item-card" onclick="window.open('${DASHBOARD_URL}', '_blank')">
      <div class="item-header">
        <span class="tag tag-emerald">${escapeHtml(job.company)}</span>
        <span style="color:#34d399; font-weight:700;">Match: ${job.match_score}%</span>
      </div>
      <div class="item-title">${escapeHtml(job.role)}</div>
      <div class="item-desc" style="display:flex; justify-content:space-between; align-items:center;">
        <span>Trust: ${job.trust_score}% (${job.trust_level === 'LOW_RISK_SIGNALS' ? 'Verified' : 'Review'})</span>
        <span style="color:#818cf8; font-weight:600;">Prepare App →</span>
      </div>
    </div>
  `).join('');
}

async function fetchStorageList() {
  try {
    const headers = await getAuthHeaders();
    const res = await fetch(`${BACKEND_URL}/storage/overview`, { headers });
    const data = await res.json();
    const container = document.getElementById('storage-list');

    const highWaste = (data.items || []).filter(i => i.waste_score >= 50).slice(0, 4);
    if (highWaste.length === 0) {
      container.innerHTML = '<div class="empty-state">Mailbox is optimized. No high waste items.</div>';
      return;
    }

    container.innerHTML = highWaste.map(item => `
      <div class="item-card" onclick="window.open('${DASHBOARD_URL}', '_blank')">
        <div class="item-header">
          <span class="tag tag-indigo">Waste: ${item.waste_score}/100</span>
          <span>${(item.size_bytes / 1024).toFixed(0)} KB</span>
        </div>
        <div class="item-title">${escapeHtml(item.subject)}</div>
        <div class="item-desc">Action: <strong style="color:#f87171;">${item.recommended_action}</strong> · ${item.reasons[0] || 'High storage footprint'}</div>
      </div>
    `).join('');
  } catch (e) {
    console.error(e);
  }
}

async function fetchApprovalsList() {
  try {
    const headers = await getAuthHeaders();
    const res = await fetch(`${BACKEND_URL}/approvals?status=PENDING`, { headers });
    const data = await res.json();
    const container = document.getElementById('approvals-list');

    if (!data || data.length === 0) {
      container.innerHTML = '<div class="empty-state">No pending actions requiring authorization.</div>';
      return;
    }

    container.innerHTML = data.slice(0, 4).map(appr => `
      <div class="item-card" onclick="window.open('${DASHBOARD_URL}', '_blank')">
        <div class="item-header">
          <span class="tag ${appr.risk_level === 'HIGH' ? 'tag-rose' : 'tag-indigo'}">Risk: ${appr.risk_level}</span>
          <span style="font-weight:700; color:#fbbf24;">Action: ${appr.action_type}</span>
        </div>
        <div class="item-title">${escapeHtml(appr.target_resource)}</div>
        <div class="item-desc">${escapeHtml(appr.reason)}</div>
      </div>
    `).join('');
  } catch (e) {
    console.error(e);
  }
}

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
