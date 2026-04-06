export default function MessageInput({ input, setInput, onSend, loading }) {
  function handleKeyPress(e) {
    if (e.key === "Enter") onSend();
  }

  return (
    <div className="input-area">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Type your message..."
      />
      <button onClick={onSend} disabled={loading}>
        Send
      </button>
    </div>
  );
}
