import React from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/main.css";

const MedicalDisclaimer = () => {
  return (
    <>
      <Navbar />
      <div className="static-page-container">
        <div className="static-page-header warning-header">
          <h1>⚠️ Medical Disclaimer</h1>
          <p className="warning-subtitle">
            Please read this carefully before using PoisonSense AI
          </p>
        </div>

        <div className="static-page-content">
          <div className="disclaimer-alert">
            <h2>🚨 CRITICAL WARNING</h2>
            <p className="large-text">
              <strong>
                IN CASE OF POISONING OR MEDICAL EMERGENCY, CALL EMERGENCY SERVICES (102) IMMEDIATELY
              </strong>
            </p>
            <p>
              PoisonSense AI is NOT a substitute for professional medical care, diagnosis,
              or treatment. DO NOT DELAY seeking immediate medical attention.
            </p>
          </div>

          <section className="policy-section">
            <h2>1. Not a Medical Service</h2>
            <p>
              PoisonSense AI provides educational information and automated symptom analysis
              using artificial intelligence. Our service:
            </p>
            <ul className="warning-list">
              <li>❌ Is NOT a licensed medical service</li>
              <li>❌ Does NOT replace poison control centers</li>
              <li>❌ Does NOT replace emergency medical services</li>
              <li>❌ Does NOT provide medical diagnoses</li>
              <li>❌ Does NOT prescribe treatments or medications</li>
              <li>❌ Should NOT be used as the sole basis for medical decisions</li>
            </ul>
          </section>

          <section className="policy-section emergency-section">
            <h2>2. Emergency Response Protocol</h2>
            <p>In case of suspected poisoning, follow these steps:</p>
            <div className="emergency-steps">
              <div className="emergency-step">
                <span className="step-number">1</span>
                <div>
                  <h3>Call Emergency Services</h3>
                  <p>
                    <strong>Dial 102</strong> (Nepal/India) immediately
                  </p>
                </div>
              </div>
              <div className="emergency-step">
                <span className="step-number">2</span>
                <div>
                  <h3>Contact Poison Control</h3>
                  <p>
                    Call your local poison control center: <strong>01-512345</strong>
                  </p>
                </div>
              </div>
              <div className="emergency-step">
                <span className="step-number">3</span>
                <div>
                  <h3>Seek Immediate Medical Care</h3>
                  <p>
                    Go to the nearest emergency department or hospital
                  </p>
                </div>
              </div>
              <div className="emergency-step">
                <span className="step-number">4</span>
                <div>
                  <h3>Use PoisonSense AI as Supplemental Information</h3>
                  <p>
                    Only after contacting emergency services, use our AI for additional guidance
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section className="policy-section">
            <h2>3. AI Limitations</h2>
            <p>
              Our artificial intelligence system has important limitations:
            </p>
            <ul>
              <li>
                <strong>Not 100% Accurate:</strong> AI predictions may contain errors or
                inaccuracies. Always verify with medical professionals.
              </li>
              <li>
                <strong>Limited Context:</strong> AI cannot fully understand your unique
                medical history, allergies, or complex health conditions.
              </li>
              <li>
                <strong>No Physical Examination:</strong> AI cannot perform physical exams,
                lab tests, or medical imaging.
              </li>
              <li>
                <strong>Training Data Limitations:</strong> AI is trained on historical data
                and may not recognize rare or emerging poisoning cases.
              </li>
              <li>
                <strong>No Legal Advice:</strong> Information provided does not constitute
                legal or professional medical advice.
              </li>
            </ul>
          </section>

          <section className="policy-section">
            <h2>4. User Responsibilities</h2>
            <p>By using PoisonSense AI, you acknowledge and agree that:</p>
            <ul>
              <li>✅ You will not delay seeking professional medical care</li>
              <li>✅ You understand AI recommendations are informational only</li>
              <li>✅ You will verify all information with qualified healthcare providers</li>
              <li>✅ You accept full responsibility for medical decisions</li>
              <li>✅ You will not rely solely on AI-generated content</li>
              <li>✅ You will call emergency services for serious symptoms</li>
            </ul>
          </section>

          <section className="policy-section">
            <h2>5. No Doctor-Patient Relationship</h2>
            <p>
              Use of PoisonSense AI does not create a doctor-patient relationship. Our
              platform does not:
            </p>
            <ul>
              <li>Provide personalized medical advice</li>
              <li>Replace consultations with healthcare professionals</li>
              <li>Establish a therapeutic relationship</li>
              <li>Guarantee treatment outcomes</li>
            </ul>
          </section>

          <section className="policy-section">
            <h2>6. Information Accuracy</h2>
            <p>
              While we strive to provide accurate and up-to-date information:
            </p>
            <ul>
              <li>⚠️ Medical knowledge constantly evolves</li>
              <li>⚠️ Content may become outdated</li>
              <li>⚠️ Regional variations in treatment exist</li>
              <li>⚠️ Individual cases may vary significantly</li>
              <li>⚠️ We do not guarantee completeness or accuracy</li>
            </ul>
            <p>
              Always consult current medical literature and healthcare providers for
              the most recent treatment guidelines.
            </p>
          </section>

          <section className="policy-section">
            <h2>7. Third-Party Information</h2>
            <p>
              Our platform may include information from third-party sources, including:
            </p>
            <ul>
              <li>Medical databases and publications</li>
              <li>WHO and health organization guidelines</li>
              <li>User-submitted content</li>
              <li>External links and resources</li>
            </ul>
            <p>
              We do not endorse or guarantee the accuracy of third-party content. Users
              should verify all information independently.
            </p>
          </section>

          <section className="policy-section">
            <h2>8. Liability Limitations</h2>
            <p>
              To the maximum extent permitted by law, PoisonSense AI and its operators:
            </p>
            <ul className="warning-list">
              <li>❌ Are NOT liable for medical outcomes</li>
              <li>❌ Are NOT liable for errors in AI recommendations</li>
              <li>❌ Are NOT liable for delayed treatment</li>
              <li>❌ Are NOT liable for reliance on platform information</li>
              <li>❌ Are NOT liable for service interruptions</li>
            </ul>
          </section>

          <section className="policy-section">
            <h2>9. Regional Considerations</h2>
            <p>
              PoisonSense AI provides information relevant to Nepal and India. Treatment
              protocols may vary by:
            </p>
            <ul>
              <li>Geographic location and regional practices</li>
              <li>Available medical resources and facilities</li>
              <li>Local regulations and guidelines</li>
              <li>Cultural and traditional medicine considerations</li>
            </ul>
            <p>
              Always follow guidance from local healthcare authorities and poison control centers.
            </p>
          </section>

          <section className="policy-section">
            <h2>10. Children and Vulnerable Populations</h2>
            <div className="warning-box">
              <p>
                <strong>Special precautions for children, elderly, pregnant women, and
                immunocompromised individuals:</strong>
              </p>
              <ul>
                <li>🚨 Poisoning affects these groups more severely</li>
                <li>🚨 Seek immediate medical attention without delay</li>
                <li>🚨 Do not attempt home remedies</li>
                <li>🚨 Call poison control and emergency services immediately</li>
              </ul>
            </div>
          </section>

          <section className="policy-section">
            <h2>11. Mental Health and Crisis Support</h2>
            <p>
              If you or someone you know is experiencing suicidal thoughts or mental health
              crisis involving potential self-harm through poisoning:
            </p>
            <div className="crisis-contacts">
              <p>📞 <strong>National Crisis Hotline: 100</strong></p>
              <p>🏥 <strong>Emergency Services: 102</strong></p>
              <p>💬 <strong>Mental Health Helpline: Available 24/7</strong></p>
            </div>
          </section>

          <section className="policy-section consent-section">
            <h2>12. Informed Consent</h2>
            <p>
              By using PoisonSense AI, you confirm that you have read, understood, and
              agree to this Medical Disclaimer. You acknowledge that:
            </p>
            <ul>
              <li>✅ You understand the limitations of AI-generated information</li>
              <li>✅ You will seek professional medical care when needed</li>
              <li>✅ You accept responsibility for your health decisions</li>
              <li>✅ You will not hold PoisonSense AI liable for medical outcomes</li>
            </ul>
          </section>

          <section className="policy-section final-warning">
            <div className="disclaimer-alert">
              <h2>⚠️ FINAL WARNING</h2>
              <p className="large-text">
                <strong>
                  IF IN DOUBT, ALWAYS SEEK IMMEDIATE MEDICAL ATTENTION
                </strong>
              </p>
              <p>
                When it comes to poisoning, minutes matter. Don't wait. Don't delay.
                Call emergency services NOW.
              </p>
              <div className="emergency-buttons">
                <a href="tel:102" className="emergency-btn">
                  📞 Call 102 (Emergency)
                </a>
                <a href="tel:015123456" className="emergency-btn secondary">
                  ☎️ Poison Control: 01-512345
                </a>
              </div>
            </div>
          </section>

          <section className="policy-section contact-section">
            <h2>Questions About This Disclaimer?</h2>
            <p>For questions or concerns, contact:</p>
            <div className="contact-info">
              <p>📧 Email: legal@poisonsense.ai</p>
              <p>📞 Phone: +977-1-5123456</p>
            </div>
          </section>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default MedicalDisclaimer;
