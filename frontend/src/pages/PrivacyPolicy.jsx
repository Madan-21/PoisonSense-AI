import React from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/main.css";

const PrivacyPolicy = () => {
  return (
    <>
      <Navbar />
      <div className="static-page-container">
        <div className="static-page-header">
          <h1>Privacy Policy</h1>
          <p>Last updated: January 28, 2026</p>
        </div>

        <div className="static-page-content">
          <section className="policy-section">
            <h2>1. Information We Collect</h2>
            <p>
              PoisonSense AI collects information to provide emergency medical services and improve
              our platform. We collect:
            </p>
            <h3>Personal Information</h3>
            <ul>
              <li>Name, email address, and phone number</li>
              <li>Date of birth and medical history (optional)</li>
              <li>Emergency contact information</li>
              <li>Location data for emergency services</li>
            </ul>
            <h3>Medical Information</h3>
            <ul>
              <li>Symptoms and poisoning incident details</li>
              <li>Analysis results and recommendations</li>
              <li>Interaction history with our AI system</li>
            </ul>
            <h3>Technical Information</h3>
            <ul>
              <li>IP address, browser type, and device information</li>
              <li>Usage patterns and analytics data</li>
              <li>Cookies and similar tracking technologies</li>
            </ul>
          </section>

          <section className="policy-section">
            <h2>2. How We Use Your Information</h2>
            <p>We use collected information to:</p>
            <ul>
              <li>🚨 Provide emergency poison identification and guidance</li>
              <li>🏥 Connect you with appropriate medical facilities</li>
              <li>📊 Improve our AI algorithms and service quality</li>
              <li>📧 Send important updates and safety alerts</li>
              <li>🔒 Maintain platform security and prevent fraud</li>
              <li>📈 Conduct research and generate anonymized statistics</li>
            </ul>
          </section>

          <section className="policy-section">
            <h2>3. Data Sharing and Disclosure</h2>
            <p>We may share your information with:</p>
            <h3>Emergency Services</h3>
            <p>
              In life-threatening situations, we share necessary information with poison control
              centers, hospitals, and emergency responders.
            </p>
            <h3>Healthcare Providers</h3>
            <p>
              With your consent, we share medical information with verified healthcare professionals
              for treatment purposes.
            </p>
            <h3>Legal Requirements</h3>
            <p>
              We may disclose information when required by law or to protect safety and rights.
            </p>
            <h3>We Never Sell Your Data</h3>
            <p>
              PoisonSense AI does not sell personal information to third parties for marketing purposes.
            </p>
          </section>

          <section className="policy-section">
            <h2>4. Data Security</h2>
            <p>
              We implement industry-standard security measures to protect your information:
            </p>
            <ul>
              <li>🔐 End-to-end encryption for sensitive data</li>
              <li>🛡️ Secure HTTPS connections</li>
              <li>🔑 JWT-based authentication</li>
              <li>💾 Regular security audits and updates</li>
              <li>🏥 HIPAA-compliant data handling</li>
            </ul>
          </section>

          <section className="policy-section">
            <h2>5. Your Rights</h2>
            <p>You have the right to:</p>
            <ul>
              <li>✅ Access your personal data</li>
              <li>✅ Correct inaccurate information</li>
              <li>✅ Request data deletion (subject to legal requirements)</li>
              <li>✅ Export your data in portable format</li>
              <li>✅ Opt-out of non-essential communications</li>
              <li>✅ Withdraw consent at any time</li>
            </ul>
          </section>

          <section className="policy-section">
            <h2>6. Cookies and Tracking</h2>
            <p>
              We use cookies and similar technologies to enhance your experience. You can control
              cookie preferences through your browser settings.
            </p>
          </section>

          <section className="policy-section">
            <h2>7. Children's Privacy</h2>
            <p>
              Our service is not directed to children under 13. We do not knowingly collect
              information from children without parental consent.
            </p>
          </section>

          <section className="policy-section">
            <h2>8. International Data Transfers</h2>
            <p>
              Your information may be processed in Nepal, India, or other countries where we
              operate. We ensure appropriate safeguards are in place.
            </p>
          </section>

          <section className="policy-section">
            <h2>9. Changes to This Policy</h2>
            <p>
              We may update this privacy policy periodically. We will notify you of significant
              changes via email or platform notification.
            </p>
          </section>

          <section className="policy-section contact-section">
            <h2>10. Contact Us</h2>
            <p>For privacy-related questions or requests, contact us at:</p>
            <div className="contact-info">
              <p>📧 Email: privacy@poisonsense.ai</p>
              <p>📞 Phone: +977-1-5123456</p>
              <p>📍 Address: Kathmandu, Nepal</p>
            </div>
          </section>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default PrivacyPolicy;
