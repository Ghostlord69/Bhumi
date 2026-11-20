import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../../app/AuthProvider";
import { api } from "../../shared/api/client";
import { formatInr, type PropertyView } from "../../shared/types";
import { Logo } from "../../shared/components/Logo";

const MIN = 1_000_000;
const MAX = 500_000_000;

export function HomePage() {
  const { session } = useAuth();
  const [params, setParams] = useSearchParams();
  const [states, setStates] = useState<string[]>([]);
  const [districts, setDistricts] = useState<string[]>([]);
  const [cities, setCities] = useState<string[]>([]);
  const [results, setResults] = useState<PropertyView[]>([]);
  const [loading, setLoading] = useState(true);
  const [recommendedMode, setRecommendedMode] = useState(false);
  const [maxPrice, setMaxPrice] = useState(Number(params.get("maxPrice") || MAX));
  const nav = useNavigate();

  const type = params.get("type") || "";
  const state = params.get("state") || "";
  const district = params.get("district") || "";
  const city = params.get("city") || "";
  const hasFilters = Boolean(type || state || district || city);

  useEffect(() => {
    api<string[]>("/api/public/locations/states").then(setStates);
  }, []);

  useEffect(() => {
    if (!state) {
      setDistricts([]);
      return;
    }
    api<string[]>(`/api/public/locations/districts?state=${encodeURIComponent(state)}`).then(setDistricts);
  }, [state]);

  useEffect(() => {
    if (!state || !district) {
      setCities([]);
      return;
    }
    api<string[]>(`/api/public/locations/cities?state=${encodeURIComponent(state)}&district=${encodeURIComponent(district)}`).then(setCities);
  }, [state, district]);

  const query = useMemo(() => {
    const q = new URLSearchParams();
    if (type) q.set("type", type);
    if (state) q.set("state", state);
    if (district) q.set("district", district);
    if (city) q.set("city", city);
    q.set("minPrice", String(MIN));
    q.set("maxPrice", String(maxPrice));
    return q.toString();
  }, [type, state, district, city, maxPrice]);

  const search = () => {
    setLoading(true);
    setRecommendedMode(false);
    api<PropertyView[]>(`/api/public/properties?${query}`)
      .then(setResults)
      .finally(() => setLoading(false));
  };

  const loadRecommended = () => {
    if (!session || session.role !== "USER") {
      search();
      return;
    }
    setLoading(true);
    setRecommendedMode(true);
    const q = new URLSearchParams();
    if (session.state) q.set("state", session.state);
    if (session.district) q.set("district", session.district);
    if (session.city) q.set("city", session.city);
    api<PropertyView[]>(`/api/public/properties/recommended?${q}`)
      .then(setResults)
      .catch(() => search())
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (!hasFilters && session?.role === "USER") {
      loadRecommended();
    } else {
      search();
    }
  }, []);

  const set = (key: string, value: string) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value); else next.delete(key);
    if (key === "state") {
      next.delete("district");
      next.delete("city");
    }
    if (key === "district") next.delete("city");
    setParams(next);
  };

  return (
    <>
      <section className="hero">
        <div className="hero-veil" aria-hidden />
        <div className="hero-copy">
          <p className="hero-brand"><Logo className="hero-logo" size="0.82em" />Bhumi</p>
          <h1>Land you can verify before you buy.</h1>
          <p className="hero-support">Public marketplace for plots, houses and flats — with city officers behind every listing.</p>
          <div className="search-card">
            <label>Type
              <select value={type} onChange={(e) => set("type", e.target.value)}>
                <option value="">All</option>
                <option value="LAND">Land</option>
                <option value="HOUSE">House</option>
                <option value="FLAT">Flat</option>
              </select>
            </label>
            <label>State
              <select value={state} onChange={(e) => set("state", e.target.value)}>
                <option value="">All states & UTs</option>
                {states.map((s) => <option key={s}>{s}</option>)}
              </select>
            </label>
            <label>District
              <select value={district} onChange={(e) => set("district", e.target.value)} disabled={!state}>
                <option value="">All districts</option>
                {districts.map((d) => <option key={d}>{d}</option>)}
              </select>
            </label>
            <label>City
              <select value={city} onChange={(e) => set("city", e.target.value)} disabled={!district}>
                <option value="">All cities</option>
                {cities.map((c) => <option key={c}>{c}</option>)}
              </select>
            </label>
            <label className="price-label">Up to {formatInr(maxPrice)}
              <input type="range" min={MIN} max={MAX} step={100000} value={maxPrice} onChange={(e) => setMaxPrice(Number(e.target.value))} />
            </label>
            <button className="btn search-go" type="button" onClick={search}>Search</button>
          </div>
        </div>
      </section>
      <section className="section marketplace">
        <div className="section-head">
          <h2>{recommendedMode ? "Recommended near you" : "Verified listings"}</h2>
          <p className="meta">{loading ? "Loading…" : `${results.length} live ${results.length === 1 ? "result" : "results"}`}</p>
        </div>
        {!loading && results.length === 0 ? (
          <p className="empty-state">No live listings match these filters. Try widening state or price.</p>
        ) : (
          <div className="grid">
            {results.map((p) => (
              <article className="card" key={p.id} onClick={() => nav(`/properties/${p.id}`)}>
                {p.coverPhotoUrl ? (
                  <img className="thumb" src={p.coverPhotoUrl} alt="" loading="lazy" />
                ) : (
                  <div className="thumb placeholder" />
                )}
                <div className="card-body">
                  <div className="eyebrow">{p.type} · {p.city}</div>
                  <div className="price">{formatInr(p.askingPrice)}</div>
                  <strong>{p.title}</strong>
                  <p className="meta">{p.address}<br />{p.measurements}</p>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </>
  );
}
