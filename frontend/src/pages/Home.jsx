import React from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import PoisonMap from "../components/PoisonMap";

export default function Home() {
  return (
    <>
      <Navbar />

      {/* HERO */}
      <section className="hero">
        <div className="hero-overlay"></div>

        <div className="hero-wrap">
          <div className="hero-left">
            <div className="badge">
              <span className="badge-dot"></span>
              Verified Medical AI • 24/7 Support
            </div>

            <h1 className="hero-title">
              Emergency
              <br />
              Poison
              <br />
              <span>Information &</span>
              <br />
              <span>AI Support</span>
            </h1>

            <p className="hero-text">
              Get immediate help for poisoning emergencies with{" "}
              <b>AI-based assessment</b>, risk evaluation, and nearby emergency
              services.
            </p>

            <div className="hero-buttons">
              <a className="btn btn-red" href="/find-help">
                ➕ Get Emergency Help Now
              </a>
              <a className="btn btn-white" href="/ai-assistant">
                ✨ Start AI Assessment
              </a>
            </div>
          </div>

          <div className="hero-right">
            <div className="glass-card">
              <img src="/images/banner.jpg" alt="AI Medical Support" />
            </div>
          </div>
        </div>
      </section>

      {/* STATS SECTION */}
      <section className="stats-section">
        <div className="stats-container">
          <div className="stat-card">
            <div className="stat-icon">👥</div>
            <h3>50K+</h3>
            <p>Users Helped</p>
          </div>
          <div className="stat-card">
            <div className="stat-icon">✓</div>
            <h3>100%</h3>
            <p>Medical AI Certified</p>
          </div>
          <div className="stat-card">
            <div className="stat-icon">⏰</div>
            <h3>24/7</h3>
            <p>Available</p>
          </div>
          <div className="stat-card">
            <div className="stat-icon">🔒</div>
            <h3>HIPAA</h3>
            <p>Compliant</p>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS SECTION */}
      <section className="how-it-works">
        <div className="section-header">
          <h2>How It Works</h2>
          <div className="underline"></div>
        </div>

        <div className="steps-container">
          <div className="step-card">
            <div className="step-number blue">1</div>
            <div className="step-icon">📋</div>
            <h3>Describe Situation</h3>
            <p>
              Tell our AI about the poisoning incident in your own language or
              voice input
            </p>
          </div>

          <div className="step-card">
            <div className="step-number green">2</div>
            <div className="step-icon">🤖</div>
            <h3>AI Assessment</h3>
            <p>
              Our AI analyzes the information and evaluates the risk instantly
            </p>
          </div>

          <div className="step-card">
            <div className="step-number red">3</div>
            <div className="step-icon">📍</div>
            <h3>Get Guidance</h3>
            <p>
              Receive nearby medical facilities and recommended next steps
              immediately
            </p>
          </div>
        </div>
      </section>

      {/* COMPREHENSIVE EMERGENCY SUPPORT SECTION */}
      <section className="features-section">
        <div className="section-header">
          <h2>Comprehensive Emergency Support</h2>
          <p>
            Everything you need to handle poisoning emergencies with confidence
          </p>
        </div>

        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon" style={{ background: "#2563eb" }}>
              💬
            </div>
            <h3>AI Chat Assistant</h3>
            <p>
              Natural language conversation to assess your emergency situation
            </p>
            <a href="#" className="learn-more">
              Learn more →
            </a>
          </div>

          <div className="feature-card">
            <div className="feature-icon" style={{ background: "#ef4444" }}>
              ⚠️
            </div>
            <h3>Risk Assessment</h3>
            <p>Evaluate symptoms and analyze immediate risk level</p>
            <a href="#" className="learn-more">
              Learn more →
            </a>
          </div>

          <div className="feature-card">
            <div className="feature-icon" style={{ background: "#f59e0b" }}>
              📋
            </div>
            <h3>Emergency Guidance</h3>
            <p>Step-by-step instructions for handling poisoning emergencies</p>
            <a href="#" className="learn-more">
              Learn more →
            </a>
          </div>

          <div className="feature-card">
            <div className="feature-icon" style={{ background: "#10b981" }}>
              📍
            </div>
            <h3>Find Nearby Help</h3>
            <p>Locate emergency rooms and poison control centers near you</p>
            <a href="#" className="learn-more">
              Learn more →
            </a>
          </div>

          <div className="feature-card">
            <div className="feature-icon" style={{ background: "#8b5cf6" }}>
              🔍
            </div>
            <h3>Poison Identification</h3>
            <p>Identify substances and understand their medical effects</p>
            <a href="#" className="learn-more">
              Learn more →
            </a>
          </div>

          <div className="feature-card">
            <div className="feature-icon" style={{ background: "#ec4899" }}>
              👤
            </div>
            <h3>Personal Profile</h3>
            <p>Store medical info and emergency contacts for quick access</p>
            <a href="#" className="learn-more">
              Learn more →
            </a>
          </div>
        </div>
      </section>

      {/* FIND NEARBY HELP SECTION */}
      <section className="find-help-section">
        <div className="section-header">
          <h2>Find Nearby Help</h2>
          <p>Locate emergency rooms and poison control centers in your area</p>
        </div>

        <div className="find-help-container">
          <div className="map-container">
            <PoisonMap />
          </div>

          <div className="help-info">
            <div className="hospital-card">
              <div className="hospital-badge">🏥 EMERGENCY</div>
              <h3>Grande Hospital, Kathmandu</h3>
              <p className="address">Fancy Street</p>
              <p className="hours">Open 24/7</p>
              <div className="hospital-buttons">
                <button className="btn-call">📞 Call Now</button>
                <button className="btn-directions">🗺️ Directions</button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ABOUT SECTION */}
      <section className="about-section">
        <div className="about-container">
          <div className="about-left">
            <img
              src="/images/home_about.jpg"
              alt="About PoisonGuard AI"
              className="about-image"
            />
          </div>

          <div className="about-right">
            <h2>About PoisonGuard AI</h2>
            <p>
              PoisonGuard AI is an advanced emergency decision support system
              designed to provide immediate, life-saving guidance during
              poisoning emergencies. Our NLP-based artificial intelligence
              analyzes your situation in real-time and delivers personalized
              emergency instructions.
            </p>
            <p>
              We combine cutting-edge natural language processing with verified
              medical databases to help you make informed decisions quickly.
              Whether you're a parent, caregiver, teacher, or first responder,
              our system is designed to support you during critical moments.
            </p>

            <div className="about-features">
              <div className="about-feature">
                <div className="about-feature-icon">✓</div>
                <div className="about-feature-content">
                  <h4>Verified Sources</h4>
                  <p>Medical databases and expert-reviewed content</p>
                </div>
              </div>

              <div className="about-feature">
                <div className="about-feature-icon">⚡</div>
                <div className="about-feature-content">
                  <h4>Instant Response</h4>
                  <p>Real-time AI analysis and guidance</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA SECTION */}
      <section className="cta-section">
        <div className="cta-container">
          <h2>Ready to Get Help?</h2>
          <p>
            Start your AI assessment now or contact emergency services
            immediately if you're in a critical situation
          </p>
          <div className="cta-buttons">
            <a href="/ai-assistant" className="cta-btn cta-btn-red">
              🏥 Start Emergency Assessment
            </a>
            <a href="tel:101" className="cta-btn cta-btn-white">
              📞 Call 101 Now
            </a>
          </div>
        </div>
      </section>

      <Footer />
    </>
  );
}
