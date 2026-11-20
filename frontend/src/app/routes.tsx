import type { ReactElement } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useAuth } from "./AuthProvider";
import { Shell } from "./Shell";
import { HomePage } from "../features/home/HomePage";
import { PropertyDetailPage } from "../features/marketplace/PropertyDetailPage";
import { LoginPage } from "../features/auth/LoginPage";
import { SignupPage } from "../features/auth/SignupPage";
import { PostPropertyPage } from "../features/documents/PostPropertyPage";
import { TrackPage } from "../features/documents/TrackPage";
import { ChatPage } from "../features/chat/ChatPage";
import { OfficerPage } from "../features/verification/OfficerPage";
import { AdminPage } from "../features/ministry/AdminPage";
import type { Role } from "../shared/types";

function roleHome(role: Role) {
  if (role === "ADMIN") return "/admin";
  if (role === "AUTHENTICATOR") return "/officer";
  return "/";
}

function Guard({ roles, children }: { roles?: Role[]; children: ReactElement }) {
  const { session } = useAuth();
  const location = useLocation();
  if (!session) {
    return <Navigate to={`/login?next=${encodeURIComponent(location.pathname + location.search)}`} replace />;
  }
  if (roles && !roles.includes(session.role)) {
    return <Navigate to={roleHome(session.role)} replace />;
  }
  return children;
}

function MarketplaceOnly({ children }: { children: ReactElement }) {
  const { session } = useAuth();
  if (session?.role === "ADMIN") return <Navigate to="/admin" replace />;
  if (session?.role === "AUTHENTICATOR") return <Navigate to="/officer" replace />;
  return children;
}

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<Shell />}>
        <Route path="/" element={<MarketplaceOnly><HomePage /></MarketplaceOnly>} />
        <Route path="/properties/:id" element={<MarketplaceOnly><PropertyDetailPage /></MarketplaceOnly>} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/sell" element={<Guard roles={["USER"]}><PostPropertyPage purpose="SALE" /></Guard>} />
        <Route path="/register-property" element={<Guard roles={["USER"]}><PostPropertyPage purpose="REGISTRY" /></Guard>} />
        <Route path="/track" element={<Guard roles={["USER"]}><TrackPage /></Guard>} />
        <Route path="/chat/:id" element={<Guard roles={["USER"]}><ChatPage /></Guard>} />
        <Route path="/officer" element={<Guard roles={["AUTHENTICATOR"]}><OfficerPage /></Guard>} />
        <Route path="/admin" element={<Guard roles={["ADMIN"]}><AdminPage /></Guard>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
