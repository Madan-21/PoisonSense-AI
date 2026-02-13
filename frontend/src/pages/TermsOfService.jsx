import React from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/main.css";

const TermsOfService = () => {
  return (
    <>
      <Navbar />
      <div className="static-page-container">
        <div className="static-page-header">
          <h1>Terms of Service</h1>
          <p>Last updated: January 28, 2026</p>
        </div>

        <div className="static-page-content">
          <section className="policy-section">
            <h2>1. Acceptance of Terms</h2>
            <p>
              By accessing and using PoisonSense AI, you accept and agree to be bound by these
              Terms of Service. If you do not agree, please do not use our services.
            </p>
          </section>

          <section className="policy-section">
            <h2>2. Service Description</h2>
            <p>
              PoisonSense AI provides AI-powered poison identification, emergency guidance, and
              connections to medical resources. Our services include:
            </p>
            <ul>
              <li>🤖 Automated symptom analysis</li>
              <li>🏥 Hospital and poison control center locator</li>
              <li>💊 Antidote availability information</li>
              <li>📚 Educational resources and safety tips</li>
              <li>👨‍⚕️ Doctor verification system</li>
            </ul>
          </section>

          <section className="policy-section warning-section">
            <h2>⚠️ 3. Medical Disclaimer</h2>
            <div className="warning-box">
              <p>
                <strong>IMPORTANT: This is NOT a substitute for professional medical care.</strong>
              </p>
              <p>
                PoisonSense AI provides informational support only. In case of poisoning
                or medical emergency:
              </p>
              <ol>
                <li>📞 <strong>Call emergency services (102) immediately</strong></li>
                <li>🏥 Seek immediate medical attention</li>
                <li>☎️ Contact your local poison control center</li>
                <li>👨‍⚕️ Consult with qualified healthcare professionals</li>
              </ol>
              <p>
                Do not rely solely on our AI system for medical decisions. Always verify
                information with licensed healthcare providers.
              </p>
            </div>
          </section>

          <section className="policy-section">
            <h2>4. User Responsibilities</h2>
            <p>As a user, you agree to:</p>
            <ul>
              <li>✅ Provide accurate information</li>
              <li>✅ Use the service for lawful purposes only</li>
              <li>✅ Maintain confidentiality of your account</li>
              <li>✅ Not misuse or attempt to hack the system</li>
              <li>✅ Respect other users' privacy</li>
              <li>✅ Follow all applicable laws and regulations</li>
            </ul>
          </section>

          <section className="policy-section">
            <h2>5. Account Registration</h2>
            <p>
              To use certain features, you must create an account. You are responsible for:
            </p>
            <ul>
              <li>Maintaining the security of your password</li>
              <li>All activities that occur under your account</li>
              <li>Notifying us of unauthorized access</li>
              <li>Providing accurate registration information</li>
            </ul>
          </section>

          <section className="policy-section">
            <h2>6. Intellectual Property</h2>
            <p>
              All content, features, and functionality of PoisonSense AI are owned by us and
              protected by copyright, trademark, and other intellectual property laws.
            </p>
            <h3>You May:</h3>
            <ul>
              <li>✅ Use the service for personal, non-commercial purposes</li>
              <li>✅ Share educational content with proper attribution</li>
            </ul>
            <h3>You May Not:</h3>
            <ul>
              <li>❌ Copy, modify, or distribute our software</li>
              <li>❌ Reverse engineer our AI algorithms</li>
              <li>❌ Remove copyright or proprietary notices</li>
              <li>❌ Use our brand without permission</li>
            </ul>
          </section>

          <section className="policy-section">
            <h2>7. Limitation of Liability</h2>
            <p>
              To the fullest extent permitted by law, PoisonSense AI and its affiliates
              shall not be liable for:
            </p>
            <ul>
              <li>Medical outcomes or treatment decisions</li>
              <li>Errors or inaccuracies in AI-generated content</li>
              <li>Service interruptions or technical issues</li>
              <li>Third-party content or links</li>
              <li>Data loss or security breaches</li>
              <li>Indirect, incidental, or consequential damages</li>
            </ul>
          </section>

          <section className="policy-section">
            <h2>8. Disclaimer of Warranties</h2>
            <p>
              PoisonSense AI is provided "as is" without warranties of any kind, express or implied,
              including but not limited to:
            </p>
            <ul>
              <li>Accuracy or completeness of information</li>
              <li>Uninterrupted or error-free operation</li>
              <li>Fitness for a particular purpose</li>
              <li>Non-infringement of third-party rights</li>
            </ul>
          </section>

          <section className="policy-section">
            <h2>9. Emergency Services</h2>
            <p>
              PoisonSense AI is not an emergency service provider. We facilitate connections
              to emergency services but do not replace:
            </p>
            <ul>
              <li>🚑 Emergency medical services (102)</li>
              <li>☎️ Poison control centers</li>
              <li>🏥 Hospital emergency departments</li>
              <li>👨‍⚕️ Licensed medical professionals</li>
            </ul>
          </section>

          <section className="policy-section">
            <h2>10. Data and Privacy</h2>
            <p>
              Your use of PoisonSense AI is subject to our Privacy Policy. By using our
              services, you consent to our data practices as described in the Privacy Policy.
            </p>
          </section>

          <section className="policy-section">
            <h2>11. Termination</h2>
            <p>
              We reserve the right to suspend or terminate your account if you:
            </p>
            <ul>
              <li>Violate these Terms of Service</li>
              <li>Engage in fraudulent or illegal activities</li>
              <li>Misuse the platform or harm other users</li>
              <li>Provide false information</li>
            </ul>
          </section>

          <section className="policy-section">
            <h2>12. Changes to Terms</h2>
            <p>
              We may modify these terms at any time. Continued use of the service after
              changes constitutes acceptance of the modified terms.
            </p>
          </section>

          <section className="policy-section">
            <h2>13. Governing Law</h2>
            <p>
              These terms are governed by the laws of Nepal. Any disputes shall be resolved
              in courts located in Kathmandu, Nepal.
            </p>
          </section>

          <section className="policy-section contact-section">
            <h2>14. Contact Information</h2>
            <p>For questions about these Terms of Service, contact us at:</p>
            <div className="contact-info">
              <p>📧 Email: legal@poisonsense.ai</p>
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

export default TermsOfService;
