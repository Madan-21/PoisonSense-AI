import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

export default function Dashboard() {
  const { user } = useAuth();

  // Role-based redirect links
  const getRoleDashboard = () => {
    switch (user?.role) {
      case "admin":
        return { path: "/admin/dashboard", label: "Admin Dashboard", icon: "🛡️" };
      case "doctor":
        return { path: "/doctor/dashboard", label: "Doctor Dashboard", icon: "🩺" };
      case "hospital_admin":
        return { path: "/hospital/dashboard", label: "Hospital Dashboard", icon: "🏥" };
      default:
        return null;
    }
  };

  const roleDashboard = getRoleDashboard();

  return (
    <>
      <Navbar />
      <div style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "60vh",
        padding: "3rem",
        textAlign: "center",
        background: "linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
      }}>
        <div style={{ fontSize: "4rem", marginBottom: "1rem" }}>👋</div>
        <h1 style={{ fontSize: "2rem", color: "#333", margin: "0 0 0.5rem 0" }}>
          Welcome, {user?.full_name || "User"}!
        </h1>
        <p style={{ color: "#666", fontSize: "1.1rem", maxWidth: "500px", lineHeight: 1.6, marginBottom: "2rem" }}>
          Your general dashboard is being built. In the meantime, explore the features below.
        </p>
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", justifyContent: "center" }}>
          {roleDashboard && (
            <Link to={roleDashboard.path} style={{
              display: "inline-flex", alignItems: "center", gap: "8px",
              padding: "12px 24px", backgroundColor: "#2563eb", color: "#fff",
              borderRadius: "8px", fontWeight: "600", textDecoration: "none",
            }}>
              {roleDashboard.icon} {roleDashboard.label}
            </Link>
          )}
          <Link to="/ai-assistant" style={{
            display: "inline-flex", alignItems: "center", gap: "8px",
            padding: "12px 24px", backgroundColor: "#059669", color: "#fff",
            borderRadius: "8px", fontWeight: "600", textDecoration: "none",
          }}>
            🧠 AI Assistant
          </Link>
          <Link to="/profile" style={{
            display: "inline-flex", alignItems: "center", gap: "8px",
            padding: "12px 24px", backgroundColor: "#6366f1", color: "#fff",
            borderRadius: "8px", fontWeight: "600", textDecoration: "none",
          }}>
            👤 My Profile
          </Link>
        </div>
      </div>
      <Footer />
    </>
  );
}