import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./AuthProvider";
import { AppRoutes } from "./routes";

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}
