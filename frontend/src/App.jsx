import { useEffect, useState } from "react";

import Sidebar from "./components/Sidebar.jsx";
import AuthPage from "./pages/AuthPage.jsx";
import ChatPage from "./pages/ChatPage.jsx";
import DocumentsPage from "./pages/DocumentsPage.jsx";
import {
  deleteConversation,
  getConversation,
  getCurrentUser,
  getAuthToken,
  listConversations,
  onUnauthorized,
  sendChatMessage,
  setAuthToken,
  uploadDocument,
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
  const [user, setUser] = useState(null);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  const [view, setView] = useState("chat");
  const [conversations, setConversations] = useState([]);
  const [isLoadingConversations, setIsLoadingConversations] = useState(true);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [activeTitle, setActiveTitle] = useState("");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [pendingImage, setPendingImage] = useState(null);
  const [notification, setNotification] = useState(null);

  const showNotification = (type, text) => {
    setNotification({ type, text });
    setTimeout(() => setNotification((current) => (current?.text === text ? null : current)), 4000);
  };

  const resetChatState = () => {
    setView("chat");
    setConversations([]);
    setActiveConversationId(null);
    setActiveTitle("");
    setMessages([]);
    setInput("");
    setPendingImage(null);
    setNotification(null);
  };

  const handleLogout = () => {
    setAuthToken(null);
    setUser(null);
    resetChatState();
  };

  // Validate any stored token once on load, and react to any 401 from the
  // API by logging out — a token can expire mid-session.
  useEffect(() => {
    onUnauthorized(handleLogout);

    const token = getAuthToken();
    if (!token) {
      setIsCheckingAuth(false);
      return;
    }
    getCurrentUser()
      .then((data) => setUser(data))
      .catch(() => setAuthToken(null))
      .finally(() => setIsCheckingAuth(false));
  }, []);

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
    if (user) refreshConversations();
  }, [user]);

  const handleAuthenticated = (authenticatedUser) => {
    setUser(authenticatedUser);
  };

  const handleNewChat = () => {
    setActiveConversationId(null);
    setActiveTitle("");
    setMessages([]);
    setInput("");
    setPendingImage(null);
    setIsSidebarOpen(false);
  };

  const handleAttachFile = async (file) => {
    if (file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = () => {
        const dataUrl = reader.result;
        const base64 = dataUrl.split(",")[1];
        setPendingImage({ name: file.name, mediaType: file.type, base64, previewUrl: dataUrl });
      };
      reader.onerror = () => showNotification("error", "Could not read that image file.");
      reader.readAsDataURL(file);
      return;
    }

    // Not an image — treat it as a document for the existing upload/RAG pipeline.
    try {
      const doc = await uploadDocument(file);
      if (doc.status === "ready") {
        const chunkLabel = doc.chunk_count === 1 ? "chunk" : "chunks";
        showNotification(
          "success",
          `📄 ${doc.filename} uploaded (${doc.chunk_count} ${chunkLabel}).`
        );
      } else {
        showNotification("error", `${doc.filename}: ${doc.error_message || "processing failed."}`);
      }
    } catch (error) {
      showNotification("error", error.message);
    }
  };

  const handleRemovePendingImage = () => setPendingImage(null);

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
    if ((!trimmed && !pendingImage) || isSending) return;

    const attachedImage = pendingImage;
    const userMessage = {
      id: `local-${nextId++}`,
      role: "user",
      text: trimmed,
      timestamp: new Date(),
      imagePreviewUrl: attachedImage?.previewUrl,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setPendingImage(null);
    setIsSending(true);

    try {
      const data = await sendChatMessage(
        trimmed,
        activeConversationId,
        attachedImage ? { data: attachedImage.base64, mediaType: attachedImage.mediaType } : null
      );
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
        const titleSource = trimmed || attachedImage?.name || "Image";
        setActiveConversationId(data.conversation_id);
        setActiveTitle(titleSource.length > 50 ? `${titleSource.slice(0, 50)}…` : titleSource);
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

  if (isCheckingAuth) {
    return <div className="auth-loading-screen">Loading…</div>;
  }

  if (!user) {
    return <AuthPage onAuthenticated={handleAuthenticated} />;
  }

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
        user={user}
        onLogout={handleLogout}
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
          pendingImage={pendingImage}
          onAttachFile={handleAttachFile}
          onRemovePendingImage={handleRemovePendingImage}
          notification={notification}
        />
      ) : (
        <DocumentsPage onMenuClick={() => setIsSidebarOpen((open) => !open)} />
      )}
    </div>
  );
}
