const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const TOKEN_STORAGE_KEY = "local_chatgpt_token";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

let authToken = null;
try {
  authToken = localStorage.getItem(TOKEN_STORAGE_KEY);
} catch {
  // localStorage can throw in some environments (private mode, etc.) — fine to skip.
}

let unauthorizedHandler = () => {};

export function setAuthToken(token) {
  authToken = token;
  try {
    if (token) localStorage.setItem(TOKEN_STORAGE_KEY, token);
    else localStorage.removeItem(TOKEN_STORAGE_KEY);
  } catch {
    // ignore storage errors; the in-memory token still works for this session
  }
}

export function getAuthToken() {
  return authToken;
}

export function onUnauthorized(handler) {
  unauthorizedHandler = handler;
}

function authHeaders() {
  return authToken ? { Authorization: `Bearer ${authToken}` } : {};
}

async function request(path, options) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json", ...authHeaders() },
      ...options,
    });
  } catch {
    throw new ApiError("Could not reach the server. Is the backend running?", 0);
  }

  if (response.status === 401) {
    unauthorizedHandler();
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

export async function registerUser(email, password) {
  return request("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function loginUser(email, password) {
  return request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function getCurrentUser() {
  return request("/auth/me");
}

export async function sendChatMessage(message, conversationId, image) {
  const data = await request("/chat", {
    method: "POST",
    body: JSON.stringify({
      message,
      conversation_id: conversationId ?? null,
      image_data: image?.data ?? null,
      image_media_type: image?.mediaType ?? null,
    }),
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

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  let response;
  try {
    response = await fetch(`${API_BASE_URL}/documents/upload`, {
      method: "POST",
      headers: { ...authHeaders() },
      body: formData,
    });
  } catch {
    throw new ApiError("Could not reach the server. Is the backend running?", 0);
  }

  if (response.status === 401) {
    unauthorizedHandler();
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = data?.detail;
    const errorMessage = typeof detail === "string" ? detail : "Something went wrong.";
    throw new ApiError(errorMessage, response.status);
  }

  return data;
}

export function listDocuments() {
  return request("/documents");
}

export function deleteDocument(documentId) {
  return request(`/documents/${documentId}`, { method: "DELETE" });
}

export async function generateImage(prompt, conversationId) {
  return request("/images/generate", {
    method: "POST",
    body: JSON.stringify({ prompt, conversation_id: conversationId ?? null }),
  });
}

export async function fetchGeneratedImageUrl(imageId) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/images/${imageId}`, {
      headers: { ...authHeaders() },
    });
  } catch {
    throw new ApiError("Could not reach the server. Is the backend running?", 0);
  }

  if (response.status === 401) {
    unauthorizedHandler();
  }
  if (!response.ok) {
    throw new ApiError("Could not load generated image.", response.status);
  }

  const blob = await response.blob();
  return URL.createObjectURL(blob);
}
