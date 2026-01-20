import React from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

export default function Signup() {
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
          <h1>📝 Sign Up</h1>
          <p>Sign up page coming soon...</p>
        </div>
      </section>
      <Footer />
    </>
  );
}
