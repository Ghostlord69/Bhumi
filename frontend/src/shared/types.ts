export type Role = "USER" | "AUTHENTICATOR" | "ADMIN";

export type Session = {
  token: string;
  userId: number;
  role: Role;
  fullName: string;
  active: boolean;
  message?: string | null;
  city?: string | null;
  district?: string | null;
  state?: string | null;
};

export type PropertyView = {
  id: number;
  sellerId: number;
  sellerName: string;
  buyerId?: number | null;
  buyerName?: string | null;
  purpose: "SALE" | "REGISTRY";
  type: "LAND" | "HOUSE" | "FLAT";
  status: string;
  title: string;
  state: string;
  district: string;
  city: string;
  address: string;
  askingPrice: number | null;
  measurements: string;
  khasraNumber?: string | null;
  ulpin?: string | null;
  surveyNumber?: string | null;
  khataNumber?: string | null;
  khewatNumber?: string | null;
  khatauniNumber?: string | null;
  houseNumber?: string | null;
  furnished?: boolean | null;
  flatNumber?: string | null;
  floor?: number | null;
  bedrooms?: number | null;
  extraNotes?: string | null;
  aiSummary?: string | null;
  officerRemarks?: string | null;
  registryPaperNames?: string[];
  coverPhotoUrl?: string | null;
  photoCount?: number;
  certificateId?: number | null;
  latitude?: number | null;
  longitude?: number | null;
  locateUrl?: string | null;
  hasVerificationReport?: boolean;
  verificationReportName?: string | null;
  hasVirtualJamabandi?: boolean;
};

export type Queues = {
  aiVerified: PropertyView[];
  physicalVerification: PropertyView[];
  registry: PropertyView[];
  pendingTransfer: PropertyView[];
};

export type NotificationView = {
  id: number;
  channel: string;
  subject: string;
  body: string;
  read: boolean;
  createdAt: string;
};

export function formatInr(value?: number | null) {
  if (value == null) {
    return "Price on request";
  }
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

export const KEY = "bhumi.session";

export function greetingFor(session: Session): string {
  if (session.role === "AUTHENTICATOR") {
    return `Hi, Authenticator of ${session.city || "your city"}`;
  }
  if (session.role === "ADMIN") {
    return `Hi, Admin of ${session.state || "your state"}`;
  }
  return `Hi, "${session.fullName}"`;
}
