import { useEffect, useState } from "react";
import { Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { clearAuth, getStoredUser, getToken, saveAuth, api } from "./api";

import LandingPage from "./pages/LandingPage";
import AuthPage from "./pages/AuthPage";
import DashboardLayout from "./components/DashboardLayout";
import Dashboard from "./pages/Dashboard";
import Labs from "./pages/Labs";
import Simulation from "./pages/Simulation";
import Assignments from "./pages/Assignments";
import Analytics from "./pages/Analytics";

function ProtectedRoute({ children }) {
  return getToken() ? children : <Navigate to="/auth" replace />;
}

function PublicRoute({ children }) {
  return getToken() ? <Navigate to="/dashboard" replace /> : children;
}

export default function App() {
  const [user, setUser] = useState(getStoredUser);

  useEffect(() => {
    if (getToken() && !user) {
      api.me()
        .then((freshUser) => {
          localStorage.setItem("engitwin_user", JSON.stringify(freshUser));
          setUser(freshUser);
        })
        .catch(() => {
          clearAuth();
          setUser(null);
        });
    }
  }, []);

  const handleAuth = (data) => {
    saveAuth(data);
    setUser(data.user);
  };

  const handleLogout = () => {
    clearAuth();
    setUser(null);
  };

  return (
    <Routes>
      <Route
        path="/"
        element={
          <PublicRoute>
            <LandingPage />
          </PublicRoute>
        }
      />

      <Route
        path="/auth"
        element={
          <PublicRoute>
            <AuthPage onAuthenticated={handleAuth} />
          </PublicRoute>
        }
      />

      <Route
        element={
          <ProtectedRoute>
            <DashboardLayout user={user} onLogout={handleLogout} />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<Dashboard user={user} />} />
        <Route path="/labs" element={<Labs user={user} />} />
        <Route path="/simulation/:experimentId" element={<Simulation />} />
        <Route path="/assignments" element={<Assignments user={user} />} />
        <Route path="/analytics" element={<Analytics />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}