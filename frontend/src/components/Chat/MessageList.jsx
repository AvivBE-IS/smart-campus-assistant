import MessageBubble from "./MessageBubble";

export default function MessageList({
  messages,
  loading,
  loadingConversation,
  activeConversationId,
  messagesEndRef,
}) {
  return (
    <div className="messages-list">
      {loadingConversation ? (
        <p className="empty-chat-state">Loading messages...</p>
      ) : messages.length === 0 && !loading ? (
        <p className="empty-chat-state">
          {activeConversationId
            ? "No messages yet. Say something!"
            : "Select a conversation or start a new chat."}
        </p>
      ) : (
        messages.map((msg, i) => (
          <div
            key={i}
            className={`message-wrapper ${msg.sender === "user" ? "user-align" : "ai-align"}`}
          >
            <MessageBubble msg={msg} />
          </div>
        ))
      )}

      {loading && (
        <div className="message-wrapper ai-align">
          <div className="message-bubble bot loading">
            <p className="message-text">Thinking...</p>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
