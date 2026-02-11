import React from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/main.css";

const TermsOfService = () => {
  return (
    <>
      <Navbar />

      <div className="tosp-page">
        {/* HERO */}
        <header className="tosp-hero">
          <div className="tosp-hero-inner">
            <h1>Terms of Service</h1>
            <p>Last updated: January 28, 2026</p>
          </div>
        </header>

        <main className="tosp-container">
          {/* 1 */}
          <section className="tosp-card">
            <div className="tosp-card-title">
              <span className="tosp-badge">1</span>
              <h2>Acceptance of Terms</h2>
            </div>
            <p className="tosp-text">
              By accessing and using PoisonSense AI, you agree to be bound by these Terms of
              Service. If you do not agree, please do not use our services.
            </p>
          </section>

          {/* 2 */}
          <section className="tosp-card">
            <div className="tosp-card-title">
              <span className="tosp-badge">2</span>
              <h2>Service Description</h2>
            </div>

            <p className="tosp-text">
              PoisonSense AI provides AI-powered poison identification, emergency guidance, and
              access to helpful resources. Our services may include:
            </p>

            <ul className="tosp-checklist">
              <li><span>🤖</span> Symptom analysis and recommendations</li>
              <li><span>🧠</span> AI-guided poison identification support</li>
              <li><span>📍</span> Nearest help center locator</li>
              <li><span>💊</span> Antidote and safety guidance</li>
              <li><span>📞</span> Emergency contact information</li>
            </ul>
          </section>

          {/* 3 - Highlight block (privacy-style) */}
          <section className="tosp-card">
            <div className="tosp-card-title">
              <span className="tosp-badge">3</span>
              <h2>Medical Disclaimer</h2>
            </div>

            <div className="tosp-highlight">
              <h3>Important Notice</h3>
              <p className="tosp-text">
                PoisonSense AI is for informational support only and does not replace professional
                medical care. In emergencies, call emergency services (e.g., 102) immediately.
              </p>

              <ul className="tosp-list">
                <li>Seek urgent medical attention</li>
                <li>Follow instructions from qualified professionals</li>
                <li>Do not rely solely on AI for medical decisions</li>
              </ul>
            </div>
          </section>

          {/* 4 */}
          <section className="tosp-card">
            <div className="tosp-card-title">
              <span className="tosp-badge">4</span>
              <h2>User Responsibilities</h2>
            </div>

            <ul className="tosp-checklist">
              <li><span>✅</span> Provide accurate information</li>
              <li><span>✅</span> Use the platform legally and responsibly</li>
              <li><span>✅</span> Keep your account credentials secure</li>
              <li><span>✅</span> Avoid misuse, fraud, or harmful behavior</li>
            </ul>
          </section>

          {/* 5 */}
          <section className="tosp-card">
            <div className="tosp-card-title">
              <span className="tosp-badge">5</span>
              <h2>Account Registration</h2>
            </div>

            <p className="tosp-text">
              Some features may require registration. You are responsible for safeguarding your
              login information and for all activities performed through your account.
            </p>
          </section>

          {/* 6 */}
          <section className="tosp-card">
            <div className="tosp-card-title">
              <span className="tosp-badge">6</span>
              <h2>Intellectual Property</h2>
            </div>

            <p className="tosp-text">
              All content and functionality within PoisonSense AI are owned by us or our licensors
              and are protected by intellectual property laws.
            </p>

            <div className="tosp-grid-2">
              <div className="tosp-subcard">
                <h3>You May</h3>
                <ul className="tosp-list">
                  <li>Use the service for personal use</li>
                  <li>Share content with proper attribution</li>
                </ul>
              </div>

              <div className="tosp-subcard">
                <h3>You May Not</h3>
                <ul className="tosp-list">
                  <li>Copy, resell, or redistribute the platform</li>
                  <li>Reverse engineer the AI system</li>
                  <li>Remove copyrights and trademarks</li>
                </ul>
              </div>
            </div>
          </section>

          {/* 7 */}
          <section className="tosp-card">
            <div className="tosp-card-title">
              <span className="tosp-badge">7</span>
              <h2>Limitation of Liability</h2>
            </div>
            <p className="tosp-text">
              To the fullest extent permitted by law, PoisonSense AI will not be liable for indirect,
              incidental, or consequential damages resulting from your use of the service.
            </p>
          </section>

          {/* 8 */}
          <section className="tosp-card">
            <div className="tosp-card-title">
              <span className="tosp-badge">8</span>
              <h2>Disclaimer of Warranties</h2>
            </div>
            <p className="tosp-text">
              PoisonSense AI is provided “as is” without warranties of any kind. We do not guarantee
              uninterrupted service or complete accuracy in all situations.
            </p>
          </section>

          {/* 9 */}
          <section className="tosp-card">
            <div className="tosp-card-title">
              <span className="tosp-badge">9</span>
              <h2>Emergency Services</h2>
            </div>
            <p className="tosp-text">
              PoisonSense AI is not an emergency service provider. We may assist you with information
              and recommended actions, but response is handled by external medical providers.
            </p>
          </section>

          {/* 10 */}
          <section className="tosp-card">
            <div className="tosp-card-title">
              <span className="tosp-badge">10</span>
              <h2>Data and Privacy</h2>
            </div>
            <p className="tosp-text">
              Use of this service is subject to our Privacy Policy. By using PoisonSense AI, you
              consent to the practices described there.
            </p>
          </section>

          {/* 11 */}
          <section className="tosp-card">
            <div className="tosp-card-title">
              <span className="tosp-badge">11</span>
              <h2>Termination</h2>
            </div>
            <p className="tosp-text">
              We reserve the right to suspend or terminate access if misuse, abuse, or violations
              of these terms are detected.
            </p>
          </section>

          {/* 12 */}
          <section className="tosp-card">
            <div className="tosp-card-title">
              <span className="tosp-badge">12</span>
              <h2>Changes to Terms</h2>
            </div>
            <p className="tosp-text">
              We may update these terms periodically. Continued use after changes indicates acceptance.
            </p>
          </section>

          {/* Contact */}
          <section className="tosp-card">
            <div className="tosp-card-title">
              <span className="tosp-badge">14</span>
              <h2>Contact Information</h2>
            </div>

            <div className="tosp-contact-box">
              <div className="tosp-contact-item">
                <span>📧</span>
                <div>
                  <strong>Email</strong>
                  <p>legal@poisonsense.ai</p>
                </div>
              </div>

              <div className="tosp-contact-item">
                <span>📞</span>
                <div>
                  <strong>Phone</strong>
                  <p>+977-1-5123456</p>
                </div>
              </div>

              <div className="tosp-contact-item">
                <span>📍</span>
                <div>
                  <strong>Address</strong>
                  <p>Kathmandu, Nepal</p>
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>

      <Footer />
    </>
  );
};

export default TermsOfService;
