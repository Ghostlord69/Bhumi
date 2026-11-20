import { KEY, type Session } from "../types";

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const raw = localStorage.getItem(KEY);
  const session = raw ? (JSON.parse(raw) as Session) : null;
  const headers = new Headers(init.headers);
  if (!(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (session?.token) {
    headers.set("Authorization", `Bearer ${session.token}`);
  }
  const res = await fetch(path, { ...init, headers });
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    throw new Error(data?.error || text || "Request failed");
  }
  return data as T;
}

export async function downloadCertificate(certificateId: number) {
  const raw = localStorage.getItem(KEY);
  const session = raw ? (JSON.parse(raw) as Session) : null;
  const res = await fetch(`/api/certificates/${certificateId}`, {
    headers: session?.token ? { Authorization: `Bearer ${session.token}` } : {},
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Could not download certificate");
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `transfer-certificate-${certificateId}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
}
