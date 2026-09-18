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
}) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="chat-page">
      <header className="chat-header">
        <button type="button" className="menu-button" onClick={onMenuClick} aria-label="Toggle conversations">
          ☰
        </button>
        <h1>{title || "New Chat"}</h1>
      </header>

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

      <form className="chat-input-form" onSubmit={onSend}>
        <input
          type="text"
          className="chat-input"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          disabled={isLoading}
        />
        <button type="submit" className="send-button" disabled={isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
