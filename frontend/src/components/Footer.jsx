import React from "react";

export default function Footer() {
  return (
    <footer className="footer ">
      <div className="footer-content">
        <div className="footer-section">
          <div className="footer-logo">
            <img
              src="/images/logo.jpg"
              alt="PoisonGuard AI Logo"
              className="logo-icon"
            />
            <h3>PoisonGuard AI</h3>
          </div>
          <p>
            Emergency poison information and
            <br />
            AI-powered decision support
            <br />
            system available 24/7.
          </p>
          <div className="social-links">
            <a href="#" aria-label="Facebook">
              f
            </a>
            <a href="#" aria-label="Twitter">
              𝕏
            </a>
            <a href="#" aria-label="Instagram">
              📷
            </a>
          </div>
        </div>

        <div className="footer-section">
          <h4>Quick Links</h4>
          <ul>
            <li>
              <a href="/">Home</a>
            </li>
            <li>
              <a href="/ai-assistant">AI Assistant</a>
            </li>
            <li>
              <a href="#risk">Risk Assessment</a>
            </li>
            <li>
              <a href="#emergency">Emergency Guidance</a>
            </li>
            <li>
              <a href="/find-help">Find Help</a>
            </li>
            <li>
              <a href="#profile">Profile</a>
            </li>
          </ul>
        </div>

        <div className="footer-section">
          <h4>Emergency Numbers</h4>
          <div className="emergency-numbers">
            <div className="emergency-item">
              <span className="label">Emergency Services</span>
              <span className="number">102</span>
            </div>
            <div className="emergency-item">
              <span className="label">Poison Control Center</span>
              <span className="number">05-123456</span>
            </div>
            <div className="emergency-item">
              <span className="label">Crisis Hotline</span>
              <span className="number">100</span>
            </div>
          </div>
        </div>

        <div className="footer-section">
          <h4>Resources</h4>
          <ul>
            <li>
              <a href="#about">About Us</a>
            </li>
            <li>
              <a href="#privacy">Privacy Policy</a>
            </li>
            <li>
              <a href="#terms">Terms of Service</a>
            </li>
            <li>
              <a href="#contact">Contact Support</a>
            </li>
            <li>
              <a href="#disclaimer">Medical Disclaimer</a>
            </li>
          </ul>
        </div>
      </div>

      <div className="footer-bottom">
        <div className="disclaimer">
          <span className="warning-icon">⚠️</span>
          <div className="disclaimer-content">
            <h5>Important Medical Disclaimer</h5>
            <p>
              This system does not replace professional medical care. In
              emergencies, contact local emergency services immediately. Always
              consult with qualified healthcare
            </p>
          </div>
        </div>
      </div>

      <div className="footer-credit">
        <p>&copy; 2026 PoisonGuard AI. All rights reserved.</p>
      </div>

      <div className="emergency-fab">
        <a href="tel:102" className="fab-button">
          📞
        </a>
      </div>
    </footer>
  );
}
