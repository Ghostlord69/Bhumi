import { FormEvent, useEffect, useState } from "react";
import { api } from "../../shared/api/client";
import type { PropertyView } from "../../shared/types";

export function PostPropertyPage({ purpose }: { purpose: "SALE" | "REGISTRY" }) {
  const [states, setStates] = useState<string[]>([]);
  const [districts, setDistricts] = useState<string[]>([]);
  const [cities, setCities] = useState<string[]>([]);
  const [papers, setPapers] = useState<FileList | null>(null);
  const [photos, setPhotos] = useState<FileList | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    type: "LAND",
    title: "",
    state: "Haryana",
    district: "Faridabad",
    city: "Ballabgarh",
    address: "",
    askingPrice: "3500000",
    measurements: "",
    khasraNumber: "",
    ulpin: "",
    registryDetail: "",
    houseNumber: "",
    furnished: "false",
    flatNumber: "",
    floor: "1",
    bedrooms: "2",
    extraNotes: "",
    latitude: "",
    longitude: "",
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
    if (!papers?.length) {
      setError("Registry papers are mandatory");
      return;
    }
    if (purpose === "SALE" && (!photos || photos.length < 3)) {
      setError("Upload at least 3 property photos (first becomes the card cover)");
      return;
    }
    if (form.ulpin && !/^[A-Za-z0-9]{14}$/.test(form.ulpin.trim())) {
      setError("ULPIN must be exactly 14 alphanumeric characters when provided");
      return;
    }
    const payload = {
      purpose,
      type: form.type,
      title: form.title,
      state: form.state,
      district: form.district,
      city: form.city,
      address: form.address,
      askingPrice: purpose === "SALE" ? Number(form.askingPrice) : null,
      measurements: form.measurements,
      khasraNumber: form.khasraNumber || null,
      ulpin: form.ulpin.trim() || null,
      registryDetail: form.registryDetail,
      houseNumber: form.houseNumber,
      furnished: form.furnished === "true",
      flatNumber: form.flatNumber,
      floor: Number(form.floor),
      bedrooms: Number(form.bedrooms),
      extraNotes: form.extraNotes,
      latitude: form.latitude ? Number(form.latitude) : null,
      longitude: form.longitude ? Number(form.longitude) : null,
    };
    const body = new FormData();
    body.append("payload", JSON.stringify(payload));
    Array.from(papers).forEach((file) => body.append("papers", file));
    if (photos) {
      Array.from(photos).forEach((file) => body.append("photos", file));
    }
    try {
      const created = await api<PropertyView>("/api/properties", { method: "POST", body });
      setMessage(`Posted. Current status: ${created.status}. ${created.aiSummary || ""}`);
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <section className="section">
      <div className="panel wide">
        <p className="eyebrow">{purpose === "SALE" ? "Marketplace" : "Registry"}</p>
        <h1>{purpose === "SALE" ? "List your property" : "Request registration"}</h1>
        <p className="meta">Papers stay private. Photos appear on the public listing.</p>
        <form className="form" onSubmit={submit}>
          <select value={form.type} onChange={(e) => set("type", e.target.value)}>
            <option value="LAND">Land</option>
            <option value="HOUSE">House</option>
            <option value="FLAT">Flat</option>
          </select>
          <input placeholder="Title" value={form.title} onChange={(e) => set("title", e.target.value)} required />
          <div className="form-row">
            <select value={form.state} onChange={(e) => set("state", e.target.value)}>{states.map((s) => <option key={s}>{s}</option>)}</select>
            <select value={form.district} onChange={(e) => set("district", e.target.value)}>{districts.map((d) => <option key={d}>{d}</option>)}</select>
          </div>
          <select value={form.city} onChange={(e) => set("city", e.target.value)}>{cities.map((c) => <option key={c}>{c}</option>)}</select>
          <input placeholder="Address" value={form.address} onChange={(e) => set("address", e.target.value)} required />
          {purpose === "SALE" && <input placeholder="Asking price (INR)" value={form.askingPrice} onChange={(e) => set("askingPrice", e.target.value)} />}
          <input placeholder="Measurements (area, plot size)" value={form.measurements} onChange={(e) => set("measurements", e.target.value)} />
          {form.type === "LAND" && (
            <>
              <input placeholder="ULPIN / Bhu-Aadhaar (optional, 14 characters)" value={form.ulpin} onChange={(e) => set("ulpin", e.target.value)} maxLength={14} />
              <input placeholder="Khasra / Survey e.g. 127/1/1 (optional if ULPIN present)" value={form.khasraNumber} onChange={(e) => set("khasraNumber", e.target.value)} />
              <p className="meta">Khasra may include subdivisions like 127/1/1. ULPIN is preferred when available.</p>
              <div className="form-row">
                <input placeholder="Latitude (optional)" value={form.latitude} onChange={(e) => set("latitude", e.target.value)} />
                <input placeholder="Longitude (optional)" value={form.longitude} onChange={(e) => set("longitude", e.target.value)} />
              </div>
              <input placeholder="Registry detail" value={form.registryDetail} onChange={(e) => set("registryDetail", e.target.value)} />
            </>
          )}
          {form.type === "HOUSE" && (
            <>
              <input placeholder="House number" value={form.houseNumber} onChange={(e) => set("houseNumber", e.target.value)} />
              <select value={form.furnished} onChange={(e) => set("furnished", e.target.value)}>
                <option value="false">Unfurnished</option>
                <option value="true">Furnished</option>
              </select>
              <input placeholder="Bedrooms" value={form.bedrooms} onChange={(e) => set("bedrooms", e.target.value)} />
            </>
          )}
          {form.type === "FLAT" && (
            <>
              <input placeholder="Flat number" value={form.flatNumber} onChange={(e) => set("flatNumber", e.target.value)} />
              <input placeholder="Floor" value={form.floor} onChange={(e) => set("floor", e.target.value)} />
              <select value={form.furnished} onChange={(e) => set("furnished", e.target.value)}>
                <option value="false">Unfurnished</option>
                <option value="true">Furnished</option>
              </select>
            </>
          )}
          <textarea placeholder="Optional notes for AI (owner name on papers, village, etc.)" value={form.extraNotes} onChange={(e) => set("extraNotes", e.target.value)} />
          <label className="file-label">Registry papers (mandatory)
            <input type="file" multiple accept="image/*,.pdf" onChange={(e) => setPapers(e.target.files)} />
          </label>
          {purpose === "SALE" && (
            <label className="file-label">Property photos (at least 3 — first is the card cover)
              <input type="file" multiple accept="image/*" onChange={(e) => setPhotos(e.target.files)} />
            </label>
          )}
          {error && <p className="error">{error}</p>}
          {message && <p className="notice">{message}</p>}
          <button className="btn" type="submit">Submit for verification</button>
        </form>
      </div>
    </section>
  );
}
