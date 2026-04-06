import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../../context/AuthContext";
import { ChatContext } from "../../context/ChatContext";

export default function Sidebar() {
  const { logout } = useContext(AuthContext);
  const {
    conversations,
    activeConversationId,
    sidebarError,
    openConversation,
    handleNewChat,
    handleDelete,
  } = useContext(ChatContext);
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  async function onNewChat() {
    try {
      await handleNewChat();
    } catch {
      // Error is surfaced in ChatContext via sidebarError
    }
  }

  async function onDelete(id, e) {
    e.stopPropagation();
    try {
      await handleDelete(id);
    } catch {
      // Silently ignore; list will reflect actual state
    }
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <span className="sidebar-logo">🎓</span>
        <span className="sidebar-name">Smart Campus</span>
      </div>

      <button className="new-chat-btn" onClick={onNewChat}>
        + New Chat
      </button>

      <div className="conversation-list">
        {sidebarError && (
          <p className="sidebar-empty" style={{ color: "#ff6b6b" }}>
            {sidebarError}
          </p>
        )}
        {!sidebarError && conversations.length === 0 ? (
          <p className="sidebar-empty">No conversations yet.</p>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              className={`conv-item ${conv.id === activeConversationId ? "active" : ""}`}
              onClick={() => openConversation(conv.id)}
            >
              <span className="conv-title">
                {conv.title || `Chat ${conv.id}`}
              </span>
              <button
                className="delete-conv-btn"
                title="Delete"
                onClick={(e) => onDelete(conv.id, e)}
              >
                ✕
              </button>
            </div>
          ))
        )}
      </div>

      <button className="logout-btn" onClick={handleLogout}>
        Logout
      </button>
    </aside>
  );
}
