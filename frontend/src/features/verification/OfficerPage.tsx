import { useEffect, useState } from "react";
import { api } from "../../shared/api/client";
import { KEY, type PropertyView, type Queues, type Session } from "../../shared/types";

async function downloadAuthed(path: string, filename: string) {
  const raw = localStorage.getItem(KEY);
  const session = raw ? (JSON.parse(raw) as Session) : null;
  const res = await fetch(path, {
    headers: session?.token ? { Authorization: `Bearer ${session.token}` } : {},
  });
  if (!res.ok) throw new Error("Download failed");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function Column({
  title,
  items,
  onDecide,
  finalize,
  onUploadReport,
  requireReport,
}: {
  title: string;
  items: PropertyView[];
  onDecide?: (id: number, approve: boolean) => void;
  finalize?: (id: number) => void;
  onUploadReport?: (id: number, file: File) => void;
  requireReport?: boolean;
}) {
  return (
    <div className="queue-col">
      <h3>{title}</h3>
      {items.map((p) => (
        <article key={p.id} className="card" style={{ marginBottom: 12 }}>
          <div className="card-body">
            <div className="eyebrow">{p.city} · {p.type}</div>
            <strong>{p.title}</strong>
            <p className="meta">{p.address}</p>
            {(p.ulpin || p.khasraNumber || p.surveyNumber || p.khataNumber) && (
              <p className="meta">
                {p.ulpin ? `ULPIN ${p.ulpin}` : null}
                {p.ulpin && p.khasraNumber ? " · " : null}
                {p.khasraNumber ? `Khasra ${p.khasraNumber}` : p.surveyNumber ? `Survey ${p.surveyNumber}` : null}
                {p.khataNumber ? ` · Khata ${p.khataNumber}` : null}
                {p.khewatNumber ? ` · Khewat ${p.khewatNumber}` : null}
              </p>
            )}
            {p.locateUrl && (
              <p className="meta">
                <a href={p.locateUrl} target="_blank" rel="noreferrer">📍 Locate</a>
              </p>
            )}
            {p.buyerName && <p className="meta">Buyer: {p.buyerName}</p>}
            <p>{p.aiSummary}</p>
            {p.registryPaperNames?.length ? <p className="meta">Papers: {p.registryPaperNames.join(", ")}</p> : null}
            {requireReport && onUploadReport && (
              <div style={{ marginBottom: 8 }}>
                <label className="file-label">
                  Physical verification report (PDF/image){p.hasVerificationReport ? ` — ${p.verificationReportName}` : " — required before approve"}
                  <input
                    type="file"
                    accept="image/*,.pdf"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) onUploadReport(p.id, file);
                    }}
                  />
                </label>
              </div>
            )}
            {onDecide && (
              <>
                <button
                  className="btn"
                  type="button"
                  disabled={requireReport && !p.hasVerificationReport}
                  onClick={() => onDecide(p.id, true)}
                >
                  Approve
                </button>
                {" "}
                <button className="btn secondary" type="button" onClick={() => onDecide(p.id, false)}>Reject</button>
              </>
            )}
            {finalize && (
              <button className="btn" type="button" onClick={() => finalize(p.id)}>Finalize ownership transfer</button>
            )}
            {p.hasVirtualJamabandi && (
              <p className="meta">
                <button
                  type="button"
                  className="btn secondary"
                  onClick={() => downloadAuthed(`/api/properties/${p.id}/virtual-jamabandi`, `virtual-jamabandi-${p.id}.png`)}
                >
                  Download virtual jamabandi
                </button>
              </p>
            )}
          </div>
        </article>
      ))}
    </div>
  );
}

export function OfficerPage() {
  const [queues, setQueues] = useState<Queues | null>(null);
  const [error, setError] = useState("");
  const load = () => api<Queues>("/api/authenticator/queues").then(setQueues);
  useEffect(() => { load(); }, []);

  const decide = async (id: number, approve: boolean) => {
    setError("");
    const remarks = approve ? "Verified in working city" : "Does not match local record";
    try {
      await api(`/api/authenticator/properties/${id}/decision?approve=${approve}&remarks=${encodeURIComponent(remarks)}`, { method: "POST" });
      load();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const uploadReport = async (id: number, file: File) => {
    setError("");
    const body = new FormData();
    body.append("report", file);
    try {
      await api(`/api/authenticator/properties/${id}/verification-report`, { method: "POST", body });
      load();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const finalize = async (id: number) => {
    await api(`/api/authenticator/properties/${id}/finalize-transfer`, { method: "POST" });
    load();
  };

  if (!queues) return <section className="section">Loading desk…</section>;

  return (
    <section className="section">
      <h1>Authenticator desk</h1>
      <p className="meta">You only see properties in your working city. Physical-visit cases need a verification report before approve. Approving generates a virtual jamabandi for government reuse.</p>
      {error && <p className="error">{error}</p>}
      <div className="queue">
        <Column title="AI verified — final approval" items={queues.aiVerified} onDecide={decide} />
        <Column
          title="AI could not match — physical visit"
          items={queues.physicalVerification}
          onDecide={decide}
          onUploadReport={uploadReport}
          requireReport
        />
        <Column title="Registry only" items={queues.registry} onDecide={decide} />
        <Column title="Ownership transfer" items={queues.pendingTransfer || []} finalize={finalize} />
      </div>
    </section>
  );
}
