import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar, NavView } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { InboxIntelligence } from './pages/InboxIntelligence';
import { StorageIntelligence } from './pages/StorageIntelligence';
import { TasksKanban } from './pages/TasksKanban';
import { JobIntelligence } from './pages/JobIntelligence';
import { ResumeView } from './pages/ResumeView';
import { CalendarView } from './pages/CalendarView';
import { ApprovalCenter } from './pages/ApprovalCenter';
import { RAGMemory } from './pages/RAGMemory';
import { AcademicDemo } from './pages/AcademicDemo';
import { AuditLogs } from './pages/AuditLogs';
import { SettingsView } from './pages/SettingsView';
import { DashboardSummary } from './types';
import { api } from './services/api';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<NavView>('dashboard');
  const [dashboardData, setDashboardData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    try {
      const data = await api.getDashboardSummary();
      setDashboardData(data);
    } catch (e) {
      console.error('Failed to load dashboard summary:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Check if URL has ?token=... from Chrome Extension
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    if (token) {
      localStorage.setItem('inboxguard_token', token);
      window.history.replaceState({}, document.title, window.location.pathname);
    }
    fetchDashboardData();
  }, []);

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard data={dashboardData} loading={loading} onNavigate={setCurrentView} />;
      case 'inbox':
        return <InboxIntelligence />;
      case 'storage':
        return <StorageIntelligence />;
      case 'tasks':
        return <TasksKanban />;
      case 'jobs':
        return <JobIntelligence />;
      case 'resume':
        return <ResumeView />;
      case 'calendar':
        return <CalendarView />;
      case 'approvals':
        return <ApprovalCenter />;
      case 'rag':
        return <RAGMemory />;
      case 'academic':
        return <AcademicDemo />;
      case 'audit':
        return <AuditLogs />;
      case 'settings':
        return <SettingsView />;
      default:
        return <Dashboard data={dashboardData} loading={loading} onNavigate={setCurrentView} />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar
        onDataRefresh={fetchDashboardData}
        pendingApprovalsCount={dashboardData?.kpis.pending_approvals ?? 0}
      />

      <div className="flex-1 flex">
        <Sidebar
          currentView={currentView}
          onSelectView={setCurrentView}
          pendingApprovalsCount={dashboardData?.kpis.pending_approvals ?? 0}
          urgentEmailsCount={dashboardData?.kpis.unread_important ?? 0}
          openTasksCount={dashboardData?.kpis.action_required ?? 0}
        />

        <main className="flex-1 overflow-y-auto bg-slate-950/90 pb-16">
          {renderView()}
        </main>
      </div>
    </div>
  );
};

export default App;
