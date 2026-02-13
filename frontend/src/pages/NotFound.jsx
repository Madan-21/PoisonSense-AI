import React from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

export default function NotFound() {
  return (
    <>
      <Navbar />
      <div style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "60vh",
        padding: "2rem",
        textAlign: "center",
        background: "linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
      }}>
        <div style={{
          fontSize: "6rem",
          marginBottom: "0.5rem",
          lineHeight: 1,
        }}>
          🚫
        </div>
        <h1 style={{
          fontSize: "3rem",
          fontWeight: "800",
          color: "#dc3545",
          margin: "0 0 0.5rem 0",
        }}>
          404
        </h1>
        <h2 style={{
          fontSize: "1.5rem",
          color: "#333",
          margin: "0 0 1rem 0",
        }}>
          Page Not Found
        </h2>
        <p style={{
          color: "#666",
          fontSize: "1.1rem",
          maxWidth: "500px",
          lineHeight: 1.6,
          marginBottom: "2rem",
        }}>
          The page you're looking for doesn't exist or has been moved.
          If this is an emergency, please call your local poison control center immediately.
        </p>
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", justifyContent: "center" }}>
          <Link
            to="/"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "8px",
              padding: "12px 28px",
              backgroundColor: "#2563eb",
              color: "#fff",
              borderRadius: "8px",
              fontWeight: "600",
              fontSize: "1rem",
              textDecoration: "none",
              transition: "background 0.2s",
            }}
          >
            🏠 Go Home
          </Link>
          <a
            href="tel:102"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "8px",
              padding: "12px 28px",
              backgroundColor: "#dc3545",
              color: "#fff",
              borderRadius: "8px",
              fontWeight: "600",
              fontSize: "1rem",
              textDecoration: "none",
              transition: "background 0.2s",
            }}
          >
            📞 Emergency: Call 102
          </a>
        </div>
      </div>
      <Footer />
    </>
  );
}
