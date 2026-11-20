import { FormEvent, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../../shared/api/client";
import { useAuth } from "../../app/AuthProvider";

type Msg = { id: number; senderId: number; senderName: string; body: string };

export function ChatPage() {
  const { id } = useParams();
  const { session } = useAuth();
  const [messages, setMessages] = useState<Msg[]>([]);
  const [body, setBody] = useState("");
  const [error, setError] = useState("");

  const load = () => api<Msg[]>(`/api/chat/${id}`).then(setMessages).catch((e) => setError(e.message));
  useEffect(() => { load(); }, [id]);

  const send = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await api(`/api/chat/${id}`, { method: "POST", body: JSON.stringify({ body }) });
      setBody("");
      load();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <section className="section">
      <div className="panel chat">
        <p className="notice">Keep the conversation on Bhumi. Phone numbers, WhatsApp and off-app payments are blocked.</p>
        <div className="chat-log">
          {messages.map((m) => (
            <div key={m.id} className={`bubble ${m.senderId === session?.userId ? "mine" : ""}`}>
              <strong>{m.senderName}</strong>
              <div>{m.body}</div>
            </div>
          ))}
        </div>
        <form className="form" onSubmit={send}>
          <input value={body} onChange={(e) => setBody(e.target.value)} placeholder="Write a respectful message" />
          {error && <p className="error">{error}</p>}
          <button className="btn" type="submit">Send</button>
        </form>
      </div>
    </section>
  );
}
