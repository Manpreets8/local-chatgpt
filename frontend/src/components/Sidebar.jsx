function formatRelativeTime(isoString) {
  const date = new Date(isoString);
  const diffMs = Date.now() - date.getTime();
  const diffMin = Math.round(diffMs / 60000);

  if (diffMin < 1) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.round(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.round(diffHr / 24);
  return `${diffDay}d ago`;
}

export default function Sidebar({
  view,
  onNavigate,
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
  isLoading,
  isOpen,
  user,
  onLogout,
}) {
  return (
    <aside className={`sidebar ${isOpen ? "sidebar--open" : ""}`}>
      <div className="sidebar-header">
        <span className="sidebar-title">Local ChatGPT</span>
      </div>

      <nav className="sidebar-nav">
        <button
          type="button"
          className={`sidebar-nav-item ${view === "chat" ? "sidebar-nav-item--active" : ""}`}
          onClick={() => onNavigate("chat")}
        >
          Chat
        </button>
        <button
          type="button"
          className={`sidebar-nav-item ${
            view === "documents" ? "sidebar-nav-item--active" : ""
          }`}
          onClick={() => onNavigate("documents")}
        >
          Documents
        </button>
      </nav>

      {view === "chat" && (
        <>
          <button type="button" className="new-chat-button" onClick={onNewChat}>
            + New Chat
          </button>

          <div className="sidebar-section-label">Conversations</div>

          <div className="conversation-list">
            {isLoading && <div className="sidebar-empty">Loading…</div>}
            {!isLoading && conversations.length === 0 && (
              <div className="sidebar-empty">No conversations yet.</div>
            )}
            {conversations.map((c) => (
              <div
                key={c.id}
                className={`conversation-item ${
                  c.id === activeConversationId ? "conversation-item--active" : ""
                }`}
                onClick={() => onSelectConversation(c.id)}
              >
                <div className="conversation-item-text">
                  <div className="conversation-item-title">{c.title}</div>
                  <div className="conversation-item-time">
                    {formatRelativeTime(c.updated_at)}
                  </div>
                </div>
                <button
                  type="button"
                  className="conversation-delete-button"
                  title="Delete conversation"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteConversation(c.id);
                  }}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </>
      )}

      {user && (
        <div className="sidebar-account">
          <span className="sidebar-account-email" title={user.email}>
            {user.email}
          </span>
          <button type="button" className="sidebar-logout-button" onClick={onLogout}>
            Log out
          </button>
        </div>
      )}
    </aside>
  );
}
