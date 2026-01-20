import React from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

export default function RiskAssessment() {
  return (
    <>
      <Navbar />
      <section
        style={{
          minHeight: "80vh",
          padding: "2rem",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <h1>⚠️ Risk Assessment</h1>
          <p>Risk assessment tool coming soon...</p>
        </div>
      </section>
      <Footer />
    </>
  );
}
