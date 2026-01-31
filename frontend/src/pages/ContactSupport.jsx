import React, { useState } from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/main.css";

const ContactSupport = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    category: "general",
    message: "",
  });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Send to backend
    console.log("Contact form submitted:", formData);
    setSubmitted(true);
    setTimeout(() => {
      setSubmitted(false);
      setFormData({
        name: "",
        email: "",
        subject: "",
        category: "general",
        message: "",
      });
    }, 3000);
  };

  return (
    <>
      <Navbar />
      <div className="static-page-container">
        <div className="static-page-header">
          <h1>Contact Support</h1>
          <p>We're here to help. Get in touch with our team.</p>
        </div>

        <div className="static-page-content">
          <div className="contact-grid">
            {/* Contact Information */}
            <div className="contact-info-section">
              <h2>Get In Touch</h2>
              <p>
                Have questions, feedback, or need assistance? Our support team is
                available 24/7 to help you.
              </p>

              <div className="contact-methods">
                <div className="contact-method">
                  <span className="contact-icon">📞</span>
                  <div>
                    <h3>Phone Support</h3>
                    <p>+977-1-5123456</p>
                    <small>24/7 availability</small>
                  </div>
                </div>

                <div className="contact-method">
                  <span className="contact-icon">📧</span>
                  <div>
                    <h3>Email Support</h3>
                    <p>support@poisonsense.ai</p>
                    <small>Response within 24 hours</small>
                  </div>
                </div>

                <div className="contact-method">
                  <span className="contact-icon">🚨</span>
                  <div>
                    <h3>Emergency Line</h3>
                    <p>102 (Emergency Services)</p>
                    <small>For immediate medical emergencies</small>
                  </div>
                </div>

                <div className="contact-method">
                  <span className="contact-icon">📍</span>
                  <div>
                    <h3>Office Location</h3>
                    <p>Kathmandu, Nepal</p>
                    <small>Mon-Fri: 9 AM - 5 PM</small>
                  </div>
                </div>
              </div>

              <div className="emergency-notice">
                <h3>⚠️ Medical Emergency?</h3>
                <p>
                  If you're experiencing a poisoning emergency, do not use this form.
                  Call emergency services immediately at <strong>102</strong> or
                  contact your nearest poison control center.
                </p>
              </div>
            </div>

            {/* Contact Form */}
            <div className="contact-form-section">
              <h2>Send Us a Message</h2>
              {submitted ? (
                <div className="success-message">
                  <span className="success-icon">✅</span>
                  <h3>Message Sent Successfully!</h3>
                  <p>
                    Thank you for contacting us. We'll get back to you within 24 hours.
                  </p>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="contact-form">
                  <div className="form-group">
                    <label htmlFor="name">Full Name *</label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      required
                      placeholder="Enter your full name"
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="email">Email Address *</label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      placeholder="your.email@example.com"
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="category">Category *</label>
                    <select
                      id="category"
                      name="category"
                      value={formData.category}
                      onChange={handleChange}
                      required
                    >
                      <option value="general">General Inquiry</option>
                      <option value="technical">Technical Support</option>
                      <option value="account">Account Issues</option>
                      <option value="feedback">Feedback</option>
                      <option value="partnership">Partnership</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label htmlFor="subject">Subject *</label>
                    <input
                      type="text"
                      id="subject"
                      name="subject"
                      value={formData.subject}
                      onChange={handleChange}
                      required
                      placeholder="Brief description of your inquiry"
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="message">Message *</label>
                    <textarea
                      id="message"
                      name="message"
                      value={formData.message}
                      onChange={handleChange}
                      required
                      rows="6"
                      placeholder="Please provide details about your inquiry..."
                    ></textarea>
                  </div>

                  <button type="submit" className="submit-btn">
                    Send Message
                  </button>
                </form>
              )}
            </div>
          </div>

          <section className="faq-section">
            <h2>Frequently Asked Questions</h2>
            <div className="faq-grid">
              <div className="faq-item">
                <h3>How quickly will I receive a response?</h3>
                <p>
                  We typically respond to all inquiries within 24 hours during business days.
                  Urgent matters are prioritized.
                </p>
              </div>
              <div className="faq-item">
                <h3>Is the service free?</h3>
                <p>
                  Yes, PoisonSense AI's core features are free for all users. We believe
                  emergency medical information should be accessible to everyone.
                </p>
              </div>
              <div className="faq-item">
                <h3>How do I report a bug or technical issue?</h3>
                <p>
                  Select "Technical Support" in the category dropdown and provide detailed
                  information about the issue you're experiencing.
                </p>
              </div>
              <div className="faq-item">
                <h3>Can I partner with PoisonSense AI?</h3>
                <p>
                  We welcome partnerships with healthcare organizations, research institutions,
                  and NGOs. Select "Partnership" to discuss collaboration opportunities.
                </p>
              </div>
            </div>
          </section>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default ContactSupport;
