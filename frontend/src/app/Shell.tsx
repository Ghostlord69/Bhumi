import { useEffect, useState } from "react";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "./AuthProvider";
import { api } from "../shared/api/client";
import { greetingFor, type NotificationView } from "../shared/types";
import { NotificationsPanel } from "../features/notifications/NotificationsPanel";
import { Logo } from "../shared/components/Logo";

export function Shell() {
  const { session, setSession } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [inboxOpen, setInboxOpen] = useState(false);
  const [unread, setUnread] = useState(0);
  const isDesk = session?.role === "ADMIN" || session?.role === "AUTHENTICATOR";

  const goGuarded = (path: string) => {
    if (!session) {
      navigate(`/login?next=${encodeURIComponent(path)}`);
      return;
    }
    navigate(path);
  };

  const loginHref = (() => {
    const path = location.pathname + location.search;
    if (path.startsWith("/login") || path.startsWith("/signup")) return "/login";
    return `/login?next=${encodeURIComponent(path)}`;
  })();

  useEffect(() => {
    if (!session?.token) {
      setUnread(0);
      return;
    }
    api<NotificationView[]>("/api/notifications")
      .then((items) => setUnread(items.filter((n) => !n.read).length))
      .catch(() => setUnread(0));
  }, [session, location.pathname, inboxOpen]);

  return (
    <div className="shell">
      <header className="header">
        <Link className="brand" to={session?.role === "ADMIN" ? "/admin" : session?.role === "AUTHENTICATOR" ? "/officer" : "/"}>
          <Logo size={34} />
          Bhumi
        </Link>
        {!isDesk && (
          <nav className="nav-center">
            <button type="button" className="nav-link" onClick={() => goGuarded("/sell")}>Sell</button>
            <button type="button" className="nav-link" onClick={() => goGuarded("/register-property")}>Register</button>
            <button type="button" className="nav-link" onClick={() => goGuarded("/track")}>Track</button>
          </nav>
        )}
        <div className="header-actions">
          {session ? (
            <>
              {session.role === "AUTHENTICATOR" && <Link to="/officer">Officer desk</Link>}
              {session.role === "ADMIN" && <Link to="/admin">Admin</Link>}
              <button className="btn secondary" type="button" onClick={() => setInboxOpen(true)}>
                Inbox{unread > 0 ? ` (${unread})` : ""}
              </button>
              <span className="greeting">{greetingFor(session)}</span>
              <button className="btn secondary" type="button" onClick={() => { setSession(null); navigate("/"); }}>Sign out</button>
            </>
          ) : (
            <>
              <Link className="ghost" to={loginHref}>Log in</Link>
              <Link className="btn" to="/signup">Sign up</Link>
            </>
          )}
        </div>
      </header>
      <Outlet />
      <NotificationsPanel open={inboxOpen} onClose={() => setInboxOpen(false)} />
    </div>
  );
}
