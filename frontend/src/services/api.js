const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request(path, options) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new ApiError("Could not reach the server. Is the backend running?", 0);
  }

  if (response.status === 204) return null;

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = data?.detail;
    const errorMessage = typeof detail === "string" ? detail : "Something went wrong.";
    throw new ApiError(errorMessage, response.status);
  }

  return data;
}

export async function sendChatMessage(message, conversationId) {
  const data = await request("/chat", {
    method: "POST",
    body: JSON.stringify({ message, conversation_id: conversationId ?? null }),
  });
  return data; // { reply, conversation_id }
}

export function listConversations() {
  return request("/conversations");
}

export function getConversation(conversationId) {
  return request(`/conversations/${conversationId}`);
}

export function deleteConversation(conversationId) {
  return request(`/conversations/${conversationId}`, { method: "DELETE" });
}
