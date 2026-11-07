
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import { AuthProvider, useAuth } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

import DashboardLayout from "./layouts/DashboardLayout";
import Dashboard from "./pages/Dashboard";
import NewEntry from "./pages/NewEntry";
import Login from "./pages/Login";
import Journal from "./pages/Journal";

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={user ? <Navigate to="/" replace /> : <Login />}
      />

      <Route element={<ProtectedRoute />}>
        <Route element={<DashboardLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/new-entry" element={<NewEntry />} />
          <Route path="/journal" element={<Journal />} />
          <Route path="/history" element={<div>Emotional History — Coming soon</div>} />
          <Route path="/patterns" element={<div>Patterns — Coming soon</div>} />
          <Route path="/voice" element={<div>Voice Journal — Coming soon</div>} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
