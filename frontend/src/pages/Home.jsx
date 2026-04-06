import { useState, useRef, useEffect, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { ChatContext } from "../context/ChatContext";
import { sendMessage } from "../services/chatService";
import Sidebar from "../components/Layout/Sidebar";
import MessageList from "../components/Chat/MessageList";
import MessageInput from "../components/Chat/MessageInput";
import "./Home.css";

export default function Home() {
  const { token } = useContext(AuthContext);
  const {
    conversations,
    activeConversationId,
    setActiveConversationId,
    messages,
    setMessages,
    loadingConversation,
    fetchConversations,
  } = useContext(ChatContext);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef(null);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, loadingConversation]);

  // Load conversation list on mount
  useEffect(() => {
    if (token) fetchConversations();
  }, [token]);

  async function handleSend() {
    const message = input.trim();
    if (!message || loading) return;
    setInput("");
    setError("");
    setMessages((prev) => [...prev, { sender: "user", text: message }]);
    setLoading(true);

    try {
      const data = await sendMessage(token, message, activeConversationId);
      if (!activeConversationId && data.conversation_id) {
        setActiveConversationId(data.conversation_id);
        await fetchConversations();
      }
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: data.response || "Sorry, I couldn't process that.",
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: err.message || "Error connecting to server." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  const activeTitle =
    conversations.find((c) => c.id === activeConversationId)?.title ||
    "Smart Campus Assistant";

  return (
    <div className="chat-page">
      {/* ── Sidebar (Layout component) ── */}
      <Sidebar />

      {/* ── Main chat area ── */}
      <div className="chat-main">
        <div className="chat-header">
          <h1>{activeTitle}</h1>
        </div>

        <div className="chat-container">
          <MessageList
            messages={messages}
            loading={loading}
            loadingConversation={loadingConversation}
            activeConversationId={activeConversationId}
            messagesEndRef={messagesEndRef}
          />

          {error && <p className="chat-error">{error}</p>}

          <MessageInput
            input={input}
            setInput={setInput}
            onSend={handleSend}
            loading={loading}
          />
        </div>
      </div>
    </div>
  );
}
