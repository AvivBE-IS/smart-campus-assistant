import { createContext, useState, useContext, useCallback } from "react";
import {
  getConversations,
  createConversation,
  getConversation,
  deleteConversation,
  mapMessage,
} from "../services/chatService";
import { AuthContext } from "./AuthContext";

export const ChatContext = createContext();

export function ChatProvider({ children }) {
  const { token } = useContext(AuthContext);

  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [sidebarError, setSidebarError] = useState("");
  const [loadingConversation, setLoadingConversation] = useState(false);

  const fetchConversations = useCallback(async () => {
    if (!token) return;
    try {
      setSidebarError("");
      const data = await getConversations(token);
      setConversations(data.conversations || []);
    } catch {
      setSidebarError("Could not load conversations.");
    }
  }, [token]);

  const openConversation = useCallback(
    async (id) => {
      setActiveConversationId(id);
      setMessages([]);
      setLoadingConversation(true);
      try {
        const data = await getConversation(token, id);
        setMessages((data.messages || []).map(mapMessage));
      } catch {
        // Error surfaced via loadingConversation + empty messages
      } finally {
        setLoadingConversation(false);
      }
    },
    [token],
  );

  const handleNewChat = useCallback(async () => {
    const data = await createConversation(token, "New Chat");
    await fetchConversations();
    setActiveConversationId(data.conversation_id);
    setMessages([]);
  }, [token, fetchConversations]);

  const handleDelete = useCallback(
    async (id) => {
      await deleteConversation(token, id);
      if (id === activeConversationId) {
        setActiveConversationId(null);
        setMessages([]);
      }
      await fetchConversations();
    },
    [token, activeConversationId, fetchConversations],
  );

  return (
    <ChatContext.Provider
      value={{
        conversations,
        activeConversationId,
        setActiveConversationId,
        messages,
        setMessages,
        sidebarError,
        loadingConversation,
        fetchConversations,
        openConversation,
        handleNewChat,
        handleDelete,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}
