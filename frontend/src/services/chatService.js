const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Maps an API message record { role, content } to the frontend shape { sender, text }.
 * role "assistant" → sender "bot", anything else → sender "user".
 */
export function mapMessage(m) {
  return {
    sender: m.role === "assistant" ? "bot" : "user",
    text: m.content,
  };
}

function authHeaders(token) {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

export async function getConversations(token) {
  const res = await fetch(`${BASE_URL}/conversations`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error("Failed to fetch conversations");
  return res.json();
}

export async function createConversation(token, title = "New Chat") {
  const res = await fetch(`${BASE_URL}/conversations`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error("Failed to create conversation");
  return res.json();
}

export async function getConversation(token, conversationId) {
  const res = await fetch(`${BASE_URL}/conversations/${conversationId}`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error("Failed to fetch conversation");
  return res.json();
}

export async function deleteConversation(token, conversationId) {
  const res = await fetch(`${BASE_URL}/conversations/${conversationId}`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error("Failed to delete conversation");
  return res.json();
}

export async function sendMessage(token, message, conversationId = null) {
  const res = await fetch(`${BASE_URL}/ask`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to send message");
  }
  return res.json();
}

export async function downloadReport(token) {
  const res = await fetch(`${BASE_URL}/report/pdf`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to generate report");
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  const disposition = res.headers.get("Content-Disposition") || "";
  // Matches: filename="quoted.pdf", filename=unquoted.pdf, filename*=UTF-8''encoded.pdf
  // Groups: [1]=full value, [2]=optional quote, [3]=quoted content, [4]=unquoted content
  const CONTENT_DISPOSITION_RE = /filename[^;=\n]*=((['"])?(.*?)\2|([^;\n]*))/i;
  const match = disposition.match(CONTENT_DISPOSITION_RE);
  a.download = match ? (match[3] || match[4] || "campus_report.pdf").trim() : "campus_report.pdf";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
