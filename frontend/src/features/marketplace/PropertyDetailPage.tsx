import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../../shared/api/client";
import { formatInr, type PropertyView } from "../../shared/types";
import { useAuth } from "../../app/AuthProvider";

export function PropertyDetailPage() {
  const { id } = useParams();
  const { session } = useAuth();
  const [property, setProperty] = useState<PropertyView | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [slide, setSlide] = useState(0);

  const load = () => api<PropertyView>(`/api/public/properties/${id}`).then(setProperty).catch((e) => setError(e.message));

  useEffect(() => { load(); }, [id]);

  const photoCount = property?.photoCount ?? 0;

  useEffect(() => {
    setSlide(0);
  }, [property?.id]);

  useEffect(() => {
    if (photoCount < 2) return;
    const timer = window.setInterval(() => {
      setSlide((s) => (s + 1) % photoCount);
    }, 4500);
    return () => window.clearInterval(timer);
  }, [photoCount, property?.id]);

  const requestPurchase = async () => {
    setError("");
    setNotice("");
    try {
      await api(`/api/properties/${id}/purchase-request`, { method: "POST" });
      setNotice("Purchase request sent. The seller must confirm, then the city verifier finalizes ownership transfer.");
    } catch (e) {
      setError((e as Error).message);
    }
  };

  if (error && !property) return <section className="section"><p className="error">{error}</p></section>;
  if (!property) return <section className="section"><p className="meta">Loading listing…</p></section>;

  const canBuy = session?.role === "USER" && session.userId !== property.sellerId;
  const photoUrl = (index: number) => `/api/public/properties/${property.id}/photos/${index}`;

  return (
    <section className="section detail-layout">
      <div className="slideshow" aria-roledescription="carousel" aria-label="Property photos">
        {photoCount > 0 ? (
          <>
            <img
              className="slideshow-image"
              src={photoUrl(slide)}
              alt={`${property.title} photo ${slide + 1} of ${photoCount}`}
            />
            {photoCount > 1 && (
              <>
                <button
                  type="button"
                  className="slideshow-nav prev"
                  aria-label="Previous photo"
                  onClick={() => setSlide((s) => (s - 1 + photoCount) % photoCount)}
                >
                  ‹
                </button>
                <button
                  type="button"
                  className="slideshow-nav next"
                  aria-label="Next photo"
                  onClick={() => setSlide((s) => (s + 1) % photoCount)}
                >
                  ›
                </button>
                <div className="slideshow-dots" role="tablist">
                  {Array.from({ length: photoCount }).map((_, i) => (
                    <button
                      key={i}
                      type="button"
                      role="tab"
                      aria-selected={i === slide}
                      aria-label={`Show photo ${i + 1}`}
                      className={i === slide ? "dot active" : "dot"}
                      onClick={() => setSlide(i)}
                    />
                  ))}
                </div>
              </>
            )}
          </>
        ) : (
          <div className="slideshow-fallback" />
        )}
      </div>

      <div className="panel detail-panel">
        <div className="eyebrow">{property.type} · {property.city}, {property.district}</div>
        <h1>{property.title}</h1>
        <p className="price">{formatInr(property.askingPrice)}</p>
        <p><strong>Location:</strong> {property.address}, {property.city}, {property.district}, {property.state}
          {property.locateUrl ? (
            <> · <a className="locate-link" href={property.locateUrl} target="_blank" rel="noreferrer" title="Open in Google Maps">📍 Locate</a></>
          ) : null}
        </p>
        <p><strong>Measurements:</strong> {property.measurements}</p>
        {property.ulpin && <p><strong>ULPIN:</strong> {property.ulpin}</p>}
        {property.houseNumber && <p><strong>House no:</strong> {property.houseNumber}</p>}
        {property.flatNumber && <p><strong>Flat:</strong> {property.flatNumber} · Floor {property.floor}</p>}
        {property.furnished != null && <p><strong>Furnished:</strong> {property.furnished ? "Yes" : "No"}</p>}
        <p className="meta">Listed by {property.sellerName}. Registry papers are visible only to the owner, AI and the local authenticator.</p>
        {notice && <p className="notice">{notice}</p>}
        {error && <p className="error">{error}</p>}
        <div className="detail-actions">
          {canBuy ? (
            <>
              <Link className="btn secondary" to={`/chat/${property.id}`}>Chat with seller</Link>
              <button className="btn" type="button" onClick={requestPurchase}>Request purchase</button>
            </>
          ) : !session ? (
            <Link className="btn" to={`/login?next=${encodeURIComponent(`/properties/${property.id}`)}`}>Log in to buy</Link>
          ) : null}
        </div>
      </div>
    </section>
  );
}
