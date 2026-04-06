export default function MessageBubble({ msg }) {
  return (
    <div className={`message-bubble ${msg.sender}`}>
      <span className="role-label">
        {msg.sender === "user" ? "You" : "Smart Assistant"}
      </span>
      <p className="message-text">{msg.text}</p>
    </div>
  );
}
