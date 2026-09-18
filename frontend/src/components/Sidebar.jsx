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
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
  isLoading,
  isOpen,
}) {
  return (
    <aside className={`sidebar ${isOpen ? "sidebar--open" : ""}`}>
      <div className="sidebar-header">
        <span className="sidebar-title">Personal AI Agent</span>
      </div>

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
              <div className="conversation-item-time">{formatRelativeTime(c.updated_at)}</div>
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
    </aside>
  );
}
