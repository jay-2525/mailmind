const BACKEND_URL = 'http://localhost:8000/api/v1';

// Check pending approvals on extension startup and interval
chrome.runtime.onInstalled.addListener(() => {
  console.log('[InboxGuard Worker] Extension installed.');
  checkPendingApprovals();
  // Set up periodic alarm for badge update
  chrome.alarms.create('checkInboxGuardApprovals', { periodInMinutes: 5 });
});

chrome.alarms.onAlarm.addListener(alarm => {
  if (alarm.name === 'checkInboxGuardApprovals') {
    checkPendingApprovals();
  }
});

async function checkPendingApprovals() {
  try {
    const res = await fetch(`${BACKEND_URL}/approvals?status=PENDING`);
    if (!res.ok) return;
    const approvals = await res.json();
    const count = approvals.length;

    if (count > 0) {
      chrome.action.setBadgeText({ text: count.toString() });
      chrome.action.setBadgeBackgroundColor({ color: '#f43f5e' }); // Rose
    } else {
      chrome.action.setBadgeText({ text: '' });
    }
  } catch (err) {
    // Offline or server not yet started
    chrome.action.setBadgeText({ text: '' });
  }
}
