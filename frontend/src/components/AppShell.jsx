import { useEffect, useState } from 'react';
import { useAuth } from '../auth/AuthContext.jsx';
import ChatPage from './ChatPage.jsx';
import ConfigurationPage from './ConfigurationPage.jsx';
import AnalyticsPage from './AnalyticsPage.jsx';

// Left-to-right order of the tab bar. `adminOnly` tabs are dropped from the DOM
// for the user role rather than rendered disabled — a disabled tab still tells
// you the feature exists.
const TABS = [
  { id: 'chat', label: 'Chat', adminOnly: false, Page: ChatPage },
  { id: 'configuration', label: 'Configuration', adminOnly: true, Page: ConfigurationPage },
  { id: 'analytics', label: 'Analytics', adminOnly: true, Page: AnalyticsPage },
];

export default function AppShell() {
  const { userId, role, isAdmin, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('chat');

  const visibleTabs = TABS.filter((tab) => isAdmin || !tab.adminOnly);

  // Chat is the one tab every role has, so fall back to it if the active tab is
  // ever not allowed — e.g. an admin session replaced by a user login.
  useEffect(() => {
    if (!TABS.some((tab) => tab.id === activeTab && (isAdmin || !tab.adminOnly))) {
      setActiveTab('chat');
    }
  }, [isAdmin, activeTab]);

  const active = visibleTabs.find((tab) => tab.id === activeTab) ?? visibleTabs[0];
  const ActivePage = active.Page;

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header-left">
          <span className="brand-dot" />
          <strong>Otto</strong>
          <span className={`role-chip ${role}`}>{role}</span>
          {userId && (
            <span className="user-chip" title={userId}>
              {userId.slice(0, 8)}
            </span>
          )}
        </div>

        <nav className="app-tabs" aria-label="Sections">
          {visibleTabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={`tab-btn ${tab.id === active.id ? 'active' : ''}`}
              aria-current={tab.id === active.id ? 'page' : undefined}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        <button className="ghost-btn" onClick={logout}>
          Log out
        </button>
      </header>

      <main className="app-main">
        <ActivePage />
      </main>
    </div>
  );
}
