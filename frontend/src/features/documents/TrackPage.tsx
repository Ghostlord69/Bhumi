import { useEffect, useState } from "react";
import { api, downloadCertificate } from "../../shared/api/client";
import { KEY, type PropertyView, type Session } from "../../shared/types";

async function downloadJamabandi(propertyId: number) {
  const raw = localStorage.getItem(KEY);
  const session = raw ? (JSON.parse(raw) as Session) : null;
  const res = await fetch(`/api/properties/${propertyId}/virtual-jamabandi`, {
    headers: session?.token ? { Authorization: `Bearer ${session.token}` } : {},
  });
  if (!res.ok) throw new Error("Could not download jamabandi");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `virtual-jamabandi-${propertyId}.png`;
  a.click();
  URL.revokeObjectURL(url);
}

function pill(status: string) {
  if (status === "LIVE" || status === "SOLD") return "pill";
  if (status === "REJECTED") return "pill bad";
  return "pill warn";
}

export function TrackPage() {
  const [items, setItems] = useState<PropertyView[]>([]);
  const [error, setError] = useState("");
  const load = () => api<PropertyView[]>("/api/properties/mine").then(setItems);
  useEffect(() => { load(); }, []);

  const confirmSale = async (id: number) => {
    setError("");
    try {
      await api(`/api/properties/${id}/confirm-sale`, { method: "POST" });
      load();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  return (
    <section className="section">
      <h1>Your properties & deals</h1>
      <p className="meta">Verified listings appear on public search. After a sale is finalized by the city verifier, the listing is removed and a transfer certificate is issued.</p>
      {error && <p className="error">{error}</p>}
      <div className="grid">
        {items.map((p) => (
          <article className="card" key={p.id}>
            <div className="card-body">
              <span className={pill(p.status)}>{p.status.replace(/_/g, " ")}</span>
              <h3>{p.title}</h3>
              <p className="meta">{p.city} · {p.address}</p>
              {(p.ulpin || p.khasraNumber || p.surveyNumber) && (
                <p className="meta">
                  {p.ulpin ? `ULPIN ${p.ulpin}` : null}
                  {p.ulpin && (p.khasraNumber || p.surveyNumber) ? " · " : null}
                  {p.khasraNumber ? `Khasra ${p.khasraNumber}` : p.surveyNumber ? `Survey ${p.surveyNumber}` : null}
                  {p.khataNumber ? ` · Khata ${p.khataNumber}` : null}
                </p>
              )}
              {p.buyerName && <p className="meta">Buyer: {p.buyerName}</p>}
              <p>{p.aiSummary}</p>
              {p.status === "PURCHASE_REQUESTED" && (
                <button className="btn" type="button" onClick={() => confirmSale(p.id)}>Confirm sale</button>
              )}
              {p.hasVirtualJamabandi && (
                <button className="btn secondary" type="button" onClick={() => downloadJamabandi(p.id)}>
                  Download virtual jamabandi
                </button>
              )}
              {p.certificateId && (
                <button className="btn secondary" type="button" onClick={() => downloadCertificate(p.certificateId!)}>
                  Download transfer certificate
                </button>
              )}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
