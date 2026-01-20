import React from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

export default function AiAssistant() {
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
          <h1>🤖 AI Assistant</h1>
          <p>AI-powered poison analysis and assessment coming soon...</p>
        </div>
      </section>
      <Footer />
    </>
  );
}
