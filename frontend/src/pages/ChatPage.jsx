import { useRef, useState } from "react";

import ChatMessage from "../components/ChatMessage.jsx";
import { sendChatMessage } from "../services/api.js";

let nextId = 1;

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleNewConversation = () => {
    setMessages([]);
    setInput("");
  };

  const handleSend = async (event) => {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    const userMessage = {
      id: nextId++,
      role: "user",
      text: trimmed,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setTimeout(scrollToBottom, 0);

    try {
      const reply = await sendChatMessage(trimmed);
      setMessages((prev) => [
        ...prev,
        { id: nextId++, role: "assistant", text: reply, timestamp: new Date() },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: nextId++,
          role: "assistant",
          text: error.message,
          timestamp: new Date(),
          isError: true,
        },
      ]);
    } finally {
      setIsLoading(false);
      setTimeout(scrollToBottom, 0);
    }
  };

  return (
    <div className="chat-page">
      <header className="chat-header">
        <h1>Personal AI Agent</h1>
        <button type="button" className="new-chat-button" onClick={handleNewConversation}>
          New Chat
        </button>
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

      <form className="chat-input-form" onSubmit={handleSend}>
        <input
          type="text"
          className="chat-input"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
        />
        <button type="submit" className="send-button" disabled={isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
