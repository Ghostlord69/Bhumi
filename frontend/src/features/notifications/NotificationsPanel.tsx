import { useEffect, useState } from "react";
import { api } from "../../shared/api/client";
import type { NotificationView } from "../../shared/types";

export function NotificationsPanel({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [items, setItems] = useState<NotificationView[]>([]);

  const load = () => api<NotificationView[]>("/api/notifications").then(setItems).catch(() => setItems([]));

  useEffect(() => {
    if (open) load();
  }, [open]);

  if (!open) return null;

  const markRead = async (id: number) => {
    await api(`/api/notifications/${id}/read`, { method: "POST" });
    load();
  };

  return (
    <div className="notify-panel" role="dialog" aria-label="Notifications">
      <div className="notify-head">
        <strong>Notifications</strong>
        <button className="btn secondary" type="button" onClick={onClose}>Close</button>
      </div>
      <div className="notify-list">
        {items.length === 0 && <p className="meta">No notifications yet.</p>}
        {items.map((n) => (
          <article key={n.id} className={`notify-item ${n.read ? "read" : ""}`}>
            <div className="eyebrow">{n.channel}</div>
            <strong>{n.subject}</strong>
            <p>{n.body}</p>
            {!n.read && (
              <button className="btn secondary" type="button" onClick={() => markRead(n.id)}>Mark read</button>
            )}
          </article>
        ))}
      </div>
    </div>
  );
}
