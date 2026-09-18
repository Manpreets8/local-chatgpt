function formatTime(date) {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function ChatMessage({ role, text, timestamp, isError, imagePreviewUrl }) {
  const isUser = role === "user";

  return (
    <div className={`message-row ${isUser ? "message-row--user" : "message-row--assistant"}`}>
      <div className={`message-bubble ${isError ? "message-bubble--error" : ""}`}>
        {imagePreviewUrl && (
          <img src={imagePreviewUrl} alt="Attached" className="message-image" />
        )}
        {text && <p className="message-text">{text}</p>}
        <span className="message-time">{formatTime(timestamp)}</span>
      </div>
    </div>
  );
}
