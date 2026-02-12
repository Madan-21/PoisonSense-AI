import React from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/main.css";

const AboutUs = () => {
  return (
    <>
      <Navbar />
      <div className="static-page-container">
        <div className="static-page-header">
          <h1>About PoisonSense AI</h1>
          <p>Advanced AI-powered poison identification and emergency response system</p>
        </div>

        <div className="static-page-content">
          <section className="about-section">
            <h2>Our Mission</h2>
            <p>
              PoisonSense AI is dedicated to saving lives through rapid, accurate poison identification
              and emergency guidance. We leverage cutting-edge artificial intelligence to provide
              immediate support during critical poisoning incidents across Nepal and India.
            </p>
          </section>

          <section className="about-section">
            <h2>What We Do</h2>
            <div className="feature-grid">
              <div className="feature-card">
                <span className="feature-icon">🤖</span>
                <h3>AI-Powered Analysis</h3>
                <p>
                  Our DistilBERT-based ML model analyzes symptoms to identify potential poisons
                  with high accuracy, providing instant recommendations.
                </p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">🏥</span>
                <h3>Emergency Network</h3>
                <p>
                  Connected to poison control centers, hospitals, and toxicology labs across
                  Nepal and India for immediate professional support.
                </p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">💊</span>
                <h3>Antidote Database</h3>
                <p>
                  Comprehensive database of antidotes with real-time availability tracking
                  at nearby medical facilities.
                </p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">📍</span>
                <h3>Location Services</h3>
                <p>
                  Find the nearest poison control centers, hospitals, and emergency services
                  based on your current location.
                </p>
              </div>
            </div>
          </section>

          <section className="about-section">
            <h2>Our Technology</h2>
            <p>
              PoisonSense AI uses state-of-the-art machine learning algorithms trained on
              comprehensive poison databases. Our system provides:
            </p>
            <ul className="feature-list">
              <li>✅ Real-time symptom analysis</li>
              <li>✅ Explainable AI with transparent reasoning</li>
              <li>✅ Multi-language support (English, Nepali, Hindi)</li>
              <li>✅ 24/7 availability</li>
              <li>✅ HIPAA-compliant data security</li>
              <li>✅ Integration with emergency services</li>
            </ul>
          </section>

          <section className="about-section">
            <h2>Our Team</h2>
            <p>
              We are a dedicated team of healthcare professionals, AI researchers, and software
              engineers committed to improving emergency medical response in South Asia. Our
              platform is developed in collaboration with:
            </p>
            <ul className="partner-list">
              <li>🏥 National Poison Control Centers</li>
              <li>🎓 Leading medical universities</li>
              <li>👨‍⚕️ Emergency medicine specialists</li>
              <li>🔬 Toxicology research institutions</li>
            </ul>
          </section>

          <section className="about-section cta-section">
            <h2>Join Us in Saving Lives</h2>
            <p>
              Whether you're a healthcare provider, researcher, or concerned citizen,
              you can contribute to our mission of making emergency poison care accessible to all.
            </p>
            <div className="cta-buttons">
              <a href="tel:102" className="cta-btn primary">Call Emergency 102</a>
              <a href="/contact" className="cta-btn secondary">Contact Us</a>
            </div>
          </section>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default AboutUs;
