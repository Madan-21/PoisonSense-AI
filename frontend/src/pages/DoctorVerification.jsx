import React from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

export default function DoctorVerification() {
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
        <div style={{ fontSize: "4rem", marginBottom: "1rem" }}>🩺</div>
        <h1 style={{ fontSize: "2rem", color: "#333", margin: "0 0 0.5rem 0" }}>
          Doctor Verification
        </h1>
        <p style={{ color: "#666", fontSize: "1.1rem", maxWidth: "500px", lineHeight: 1.6 }}>
          This feature is under development. Verified doctors will have access to advanced clinical tools and case management features.
        </p>
      </div>
      <Footer />
    </>
  );
}
