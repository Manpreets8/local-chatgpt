import { useEffect, useState } from "react";

import Sidebar from "./components/Sidebar.jsx";
import ChatPage from "./pages/ChatPage.jsx";
import DocumentsPage from "./pages/DocumentsPage.jsx";
import {
  deleteConversation,
  getConversation,
  listConversations,
  sendChatMessage,
} from "./services/api.js";

let nextId = 1;

function messagesFromHistory(history) {
  return history.map((m) => ({
    id: `${m.id}`,
    role: m.role,
    text: m.content,
    timestamp: new Date(m.created_at),
  }));
}

export default function App() {
  const [view, setView] = useState("chat");
  const [conversations, setConversations] = useState([]);
  const [isLoadingConversations, setIsLoadingConversations] = useState(true);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [activeTitle, setActiveTitle] = useState("");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const refreshConversations = async () => {
    try {
      const data = await listConversations();
      setConversations(data);
    } catch {
      // sidebar list is non-critical; fail silently and let the user keep chatting
    } finally {
      setIsLoadingConversations(false);
    }
  };

  useEffect(() => {
    refreshConversations();
  }, []);

  const handleNewChat = () => {
    setActiveConversationId(null);
    setActiveTitle("");
    setMessages([]);
    setInput("");
    setIsSidebarOpen(false);
  };

  const handleSelectConversation = async (conversationId) => {
    try {
      const data = await getConversation(conversationId);
      setActiveConversationId(data.id);
      setActiveTitle(data.title);
      setMessages(messagesFromHistory(data.messages));
      setIsSidebarOpen(false);
    } catch {
      // if it failed to load (e.g. deleted elsewhere), just refresh the list
      refreshConversations();
    }
  };

  const handleDeleteConversation = async (conversationId) => {
    try {
      await deleteConversation(conversationId);
    } catch {
      // ignore; list refresh below reflects real state either way
    }
    if (conversationId === activeConversationId) {
      handleNewChat();
    }
    refreshConversations();
  };

  const handleSend = async (event) => {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isSending) return;

    const userMessage = {
      id: `local-${nextId++}`,
      role: "user",
      text: trimmed,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsSending(true);

    try {
      const data = await sendChatMessage(trimmed, activeConversationId);
      setMessages((prev) => [
        ...prev,
        {
          id: `local-${nextId++}`,
          role: "assistant",
          text: data.reply,
          timestamp: new Date(),
        },
      ]);
      if (activeConversationId === null) {
        setActiveConversationId(data.conversation_id);
        setActiveTitle(trimmed.length > 50 ? `${trimmed.slice(0, 50)}…` : trimmed);
      }
      refreshConversations();
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: `local-${nextId++}`,
          role: "assistant",
          text: error.message,
          timestamp: new Date(),
          isError: true,
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const handleNavigate = (nextView) => {
    setView(nextView);
    setIsSidebarOpen(false);
  };

  return (
    <div className="app-layout">
      <Sidebar
        view={view}
        onNavigate={handleNavigate}
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={(id) => {
          setView("chat");
          handleSelectConversation(id);
        }}
        onNewChat={handleNewChat}
        onDeleteConversation={handleDeleteConversation}
        isLoading={isLoadingConversations}
        isOpen={isSidebarOpen}
      />
      {isSidebarOpen && (
        <div className="sidebar-overlay" onClick={() => setIsSidebarOpen(false)} />
      )}
      {view === "chat" ? (
        <ChatPage
          title={activeTitle}
          messages={messages}
          isLoading={isSending}
          input={input}
          onInputChange={setInput}
          onSend={handleSend}
          onMenuClick={() => setIsSidebarOpen((open) => !open)}
        />
      ) : (
        <DocumentsPage onMenuClick={() => setIsSidebarOpen((open) => !open)} />
      )}
    </div>
  );
}
