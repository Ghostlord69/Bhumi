import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import { KEY, type Session } from "../shared/types";

type AuthState = {
  session: Session | null;
  setSession: (session: Session | null) => void;
};

const Ctx = createContext<AuthState>({ session: null, setSession: () => undefined });

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSessionState] = useState<Session | null>(() => {
    const raw = localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as Session) : null;
  });
  const setSession = (next: Session | null) => {
    if (next) {
      localStorage.setItem(KEY, JSON.stringify(next));
    } else {
      localStorage.removeItem(KEY);
    }
    setSessionState(next);
  };
  const value = useMemo(() => ({ session, setSession }), [session]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useAuth() {
  return useContext(Ctx);
}
