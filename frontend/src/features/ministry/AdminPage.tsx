import { useEffect, useState } from "react";
import { api } from "../../shared/api/client";

type Application = {
  id: number;
  fullName: string;
  personalEmail: string;
  phone?: string;
  officialIdNumber: string;
  city: string;
  district: string;
  state: string;
  status: string;
};

type Dashboard = {
  adminId: number;
  adminName: string;
  stateUnionTerritory: string;
  email: string;
  phone: string;
  activeAuthenticators: {
    id: number;
    fullName: string;
    officialLogin: string;
    city: string;
    district: string;
    state: string;
  }[];
  pendingApplications: Application[];
  rejectedApplications: Application[];
};

export function AdminPage() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const load = () => api<Dashboard>("/api/admin/dashboard").then(setData).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  const approve = async (id: number) => {
    setError("");
    await api(`/api/admin/applications/${id}/approve`, { method: "POST" });
    setNotice("Official login issued. Check Inbox / backend console for the email to the applicant.");
    load();
  };

  const reject = async (id: number) => {
    setError("");
    const remarks = window.prompt("Rejection remarks (optional)", "") ?? "";
    await api(`/api/admin/applications/${id}/reject?remarks=${encodeURIComponent(remarks)}`, { method: "POST" });
    setNotice("Application rejected. The applicant was notified.");
    load();
  };

  if (error && !data) return <section className="section"><p className="error">{error}</p></section>;
  if (!data) return <section className="section">Loading…</section>;

  return (
    <section className="section">
      <h1>State admin desk</h1>
      <p className="meta">
        Admin ID {data.adminId} · {data.adminName} · {data.stateUnionTerritory}
        <br />
        {data.email} · {data.phone}
      </p>
      <p className="meta">You only see authenticator applications and officers for <strong>{data.stateUnionTerritory}</strong> (same idea as city-scoped verifiers).</p>
      {notice && <p className="notice">{notice}</p>}
      {error && <p className="error">{error}</p>}
      <div className="queue" style={{ gridTemplateColumns: "repeat(3, 1fr)" }}>
        <div className="queue-col">
          <h3>Pending verifier applications</h3>
          {data.pendingApplications.length === 0 && <p className="meta">No pending applications in your state.</p>}
          {data.pendingApplications.map((a) => (
            <article key={a.id} className="card" style={{ marginBottom: 12 }}>
              <div className="card-body">
                <strong>{a.fullName}</strong>
                <p className="meta">{a.personalEmail} · {a.phone || "no phone"}</p>
                <p className="meta">ID {a.officialIdNumber}</p>
                <p className="meta">{a.city}, {a.district}, {a.state}</p>
                <button className="btn" type="button" onClick={() => approve(a.id)}>Approve</button>
                {" "}
                <button className="btn secondary" type="button" onClick={() => reject(a.id)}>Reject</button>
              </div>
            </article>
          ))}
        </div>
        <div className="queue-col">
          <h3>Active authenticators in state</h3>
          {data.activeAuthenticators.map((a) => (
            <p key={a.id}>
              <strong>{a.fullName}</strong><br />
              {a.officialLogin}<br />
              City: {a.city} · {a.district}
            </p>
          ))}
        </div>
        <div className="queue-col">
          <h3>Rejected applications</h3>
          {data.rejectedApplications.length === 0 && <p className="meta">None yet.</p>}
          {data.rejectedApplications.map((a) => (
            <p key={a.id} className="meta">
              <strong>{a.fullName}</strong><br />
              {a.city}, {a.district} · {a.personalEmail}
            </p>
          ))}
        </div>
      </div>
    </section>
  );
}
