import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../../shared/api/client";
import { useAuth } from "../../app/AuthProvider";
import type { Session } from "../../shared/types";

export function SignupPage() {
  const [mode, setMode] = useState<"USER" | "AUTH">("USER");
  const [states, setStates] = useState<string[]>([]);
  const [districts, setDistricts] = useState<string[]>([]);
  const [cities, setCities] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const { setSession } = useAuth();
  const nav = useNavigate();
  const [form, setForm] = useState({
    fullName: "", email: "", phone: "", password: "",
    officialIdNumber: "", state: "Haryana", district: "Faridabad", city: "Ballabgarh",
  });

  useEffect(() => { api<string[]>("/api/public/locations/states").then(setStates); }, []);
  useEffect(() => {
    api<string[]>(`/api/public/locations/districts?state=${encodeURIComponent(form.state)}`).then(setDistricts);
  }, [form.state]);
  useEffect(() => {
    api<string[]>(`/api/public/locations/cities?state=${encodeURIComponent(form.state)}&district=${encodeURIComponent(form.district)}`).then(setCities);
  }, [form.state, form.district]);

  const set = (key: string, value: string) => setForm((f) => ({ ...f, [key]: value }));

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      if (mode === "AUTH") {
        const res = await api<Session>("/api/auth/authenticator-apply", {
          method: "POST",
          body: JSON.stringify({
            fullName: form.fullName,
            personalEmail: form.email,
            phone: form.phone,
            password: form.password,
            officialIdNumber: form.officialIdNumber,
            state: form.state,
            district: form.district,
            city: form.city,
          }),
        });
        setMessage(res.message || "Submitted for state admin approval.");
        return;
      }
      const session = await api<Session>("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({
          fullName: form.fullName,
          email: form.email,
          phone: form.phone,
          password: form.password,
          role: "USER",
        }),
      });
      setSession(session);
      nav("/");
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <section className="auth-stage">
      <div className="auth-panel">
        <p className="eyebrow">Join Bhumi</p>
        <h1>Create your account</h1>
        <div className="login-tabs" role="tablist">
          <button type="button" className={mode === "USER" ? "login-tab active" : "login-tab"} onClick={() => setMode("USER")}>User</button>
          <button type="button" className={mode === "AUTH" ? "login-tab active" : "login-tab"} onClick={() => setMode("AUTH")}>Authenticator</button>
        </div>
        <p className="meta">{mode === "USER" ? "One account to buy and sell verified land." : "Apply as Patwari/Tehsildar. A state admin must approve you."}</p>
        <form className="form" onSubmit={submit}>
          <input placeholder="Full name" value={form.fullName} onChange={(e) => set("fullName", e.target.value)} required />
          <input placeholder={mode === "AUTH" ? "Personal email" : "Email"} value={form.email} onChange={(e) => set("email", e.target.value)} required />
          <input placeholder="Phone" value={form.phone} onChange={(e) => set("phone", e.target.value)} required />
          <input placeholder="Password" type="password" value={form.password} onChange={(e) => set("password", e.target.value)} required />
          {mode === "AUTH" && (
            <>
              <input placeholder="Official ID number" value={form.officialIdNumber} onChange={(e) => set("officialIdNumber", e.target.value)} required />
              <select value={form.state} onChange={(e) => set("state", e.target.value)}>{states.map((s) => <option key={s}>{s}</option>)}</select>
              <select value={form.district} onChange={(e) => set("district", e.target.value)}>{districts.map((d) => <option key={d}>{d}</option>)}</select>
              <select value={form.city} onChange={(e) => set("city", e.target.value)}>{cities.map((c) => <option key={c}>{c}</option>)}</select>
            </>
          )}
          {error && <p className="error">{error}</p>}
          {message && <p className="notice">{message}</p>}
          <button className="btn" type="submit">{mode === "AUTH" ? "Submit for approval" : "Sign up"}</button>
        </form>
        <p className="meta">Already have an account? <Link to="/login">Log in</Link></p>
      </div>
    </section>
  );
}
