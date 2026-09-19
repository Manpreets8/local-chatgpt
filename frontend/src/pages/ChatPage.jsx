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
  composerMode,
  onSetComposerMode,
  notification,
}) {
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const isImageMode = composerMode === "image";

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
          <div className="chat-empty-state">
            {isImageMode ? "Describe an image to generate." : "Ask me anything to get started."}
          </div>
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

      {pendingImage && !isImageMode && (
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

      <div className="composer-mode-toggle">
        <button
          type="button"
          className={`mode-toggle-button ${!isImageMode ? "mode-toggle-button--active" : ""}`}
          onClick={() => onSetComposerMode("chat")}
        >
          💬 Chat
        </button>
        <button
          type="button"
          className={`mode-toggle-button ${isImageMode ? "mode-toggle-button--active" : ""}`}
          onClick={() => onSetComposerMode("image")}
          title="Generate a new AI image from a text description"
        >
          🎨 Generate Image
        </button>
      </div>

      <form className="chat-input-form" onSubmit={onSend}>
        {!isImageMode && (
          <>
            <input
              ref={fileInputRef}
              type="file"
              id="chat-attach-input"
              accept="image/png,image/jpeg,image/webp,image/gif,.pdf,.txt,.docx"
              onChange={handleFileChange}
              hidden
            />
            <label
              htmlFor="chat-attach-input"
              className="attach-button"
              title="Attach a photo or document"
            >
              +
            </label>
          </>
        )}
        <input
          type="text"
          className="chat-input"
          placeholder={
            isImageMode ? "Describe the image you want (e.g. 3D Pixar-style robot)…" : "Type a message..."
          }
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          disabled={isLoading}
        />
        <button
          type="submit"
          className="send-button"
          disabled={isLoading || (!input.trim() && !(pendingImage && !isImageMode))}
        >
          Send
        </button>
      </form>
    </div>
  );
}
