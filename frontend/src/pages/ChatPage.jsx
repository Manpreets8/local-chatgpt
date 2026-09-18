import { useEffect, useRef } from "react";

import ChatMessage from "../components/ChatMessage.jsx";

export default function ChatPage({
  title,
  messages,
  isLoading,
  input,
  onInputChange,
  onSend,
  onMenuClick,
  pendingImage,
  onAttachFile,
  onRemovePendingImage,
  notification,
}) {
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    if (file) onAttachFile(file);
    event.target.value = "";
  };

  return (
    <div className="chat-page">
      <header className="chat-header">
        <button type="button" className="menu-button" onClick={onMenuClick} aria-label="Toggle conversations">
          ☰
        </button>
        <h1>{title || "New Chat"}</h1>
      </header>

      {notification && (
        <div className={`chat-notification chat-notification--${notification.type}`}>
          {notification.text}
        </div>
      )}

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty-state">Ask me anything to get started.</div>
        )}
        {messages.map((m) => (
          <ChatMessage
            key={m.id}
            role={m.role}
            text={m.text}
            timestamp={m.timestamp}
            isError={m.isError}
            imagePreviewUrl={m.imagePreviewUrl}
          />
        ))}
        {isLoading && (
          <div className="message-row message-row--assistant">
            <div className="message-bubble message-bubble--loading">
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-dot" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {pendingImage && (
        <div className="pending-attachment">
          <img src={pendingImage.previewUrl} alt="Selected attachment" />
          <span className="pending-attachment-name">{pendingImage.name}</span>
          <button
            type="button"
            className="pending-attachment-remove"
            onClick={onRemovePendingImage}
            aria-label="Remove attachment"
          >
            ×
          </button>
        </div>
      )}

      <form className="chat-input-form" onSubmit={onSend}>
        <input
          ref={fileInputRef}
          type="file"
          id="chat-attach-input"
          accept="image/png,image/jpeg,image/webp,image/gif,.pdf,.txt,.docx"
          onChange={handleFileChange}
          hidden
        />
        <label htmlFor="chat-attach-input" className="attach-button" title="Attach a photo or document">
          +
        </label>
        <input
          type="text"
          className="chat-input"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          disabled={isLoading}
        />
        <button
          type="submit"
          className="send-button"
          disabled={isLoading || (!input.trim() && !pendingImage)}
        >
          Send
        </button>
      </form>
    </div>
  );
}
