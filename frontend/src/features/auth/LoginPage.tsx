import { FormEvent, useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../../shared/api/client";
import { useAuth } from "../../app/AuthProvider";
import type { Role, Session } from "../../shared/types";
import { Logo } from "../../shared/components/Logo";

type Tab = "USER" | "AUTHENTICATOR" | "ADMIN";

function safeNext(raw: string | null, role: Role): string {
  const fallback = role === "ADMIN" ? "/admin" : role === "AUTHENTICATOR" ? "/officer" : "/";
  if (!raw || !raw.startsWith("/") || raw.startsWith("//") || raw.startsWith("/login") || raw.startsWith("/signup")) {
    return fallback;
  }
  if (role === "USER" && (raw.startsWith("/admin") || raw.startsWith("/officer"))) return "/";
  if (role === "AUTHENTICATOR") {
    if (raw.startsWith("/admin") || raw === "/" || raw.startsWith("/properties") || raw.startsWith("/sell") || raw.startsWith("/track") || raw.startsWith("/register")) {
      return "/officer";
    }
  }
  if (role === "ADMIN") {
    if (raw.startsWith("/officer") || raw === "/" || raw.startsWith("/properties") || raw.startsWith("/sell") || raw.startsWith("/track") || raw.startsWith("/register")) {
      return "/admin";
    }
  }
  return raw;
}

export function LoginPage() {
  const [tab, setTab] = useState<Tab>("USER");
  const [email, setEmail] = useState("user@bhumi.test");
  const [password, setPassword] = useState("User@123");
  const [error, setError] = useState("");
  const { setSession } = useAuth();
  const nav = useNavigate();
  const [params] = useSearchParams();

  const hint = useMemo(() => {
    if (tab === "USER") return "Demo: user@bhumi.test / User@123";
    if (tab === "AUTHENTICATOR") return "Demo: auth.ballabgarh@bhumi.gov.in / Auth@123";
    return "Admins: {RTO}12345{reverse}@bhumi.gov.in · password Admin{RTO}123@ · e.g. HR12345RH@bhumi.gov.in / AdminHR123@";
  }, [tab]);

  const switchTab = (next: Tab) => {
    setTab(next);
    setError("");
    if (next === "USER") {
      setEmail("user@bhumi.test");
      setPassword("User@123");
    } else if (next === "AUTHENTICATOR") {
      setEmail("auth.ballabgarh@bhumi.gov.in");
      setPassword("Auth@123");
    } else {
      setEmail("HR12345RH@bhumi.gov.in");
      setPassword("AdminHR123@");
    }
  };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const session = await api<Session>("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      setSession(session);
      nav(safeNext(params.get("next"), session.role));
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <section className="auth-stage">
      <div className="auth-panel">
        <div className="auth-brand">
          <Logo size={52} />
          <span>Bhumi</span>
        </div>
        <p className="eyebrow">Welcome back</p>
        <h1>Sign in to Bhumi</h1>
        <div className="login-tabs" role="tablist">
          {(["USER", "AUTHENTICATOR", "ADMIN"] as Tab[]).map((t) => (
            <button
              key={t}
              type="button"
              role="tab"
              className={tab === t ? "login-tab active" : "login-tab"}
              onClick={() => switchTab(t)}
            >
              {t === "USER" ? "User" : t === "AUTHENTICATOR" ? "Authenticator" : "Admin"}
            </button>
          ))}
        </div>
        <form className="form" onSubmit={submit}>
          <input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <input placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          {error && <p className="error">{error}</p>}
          <button className="btn" type="submit">Log in</button>
        </form>
        <p className="meta">New here? <Link to="/signup">Create a user account</Link> or apply as authenticator on signup.</p>
        <p className="notice">{hint}</p>
      </div>
    </section>
  );
}
