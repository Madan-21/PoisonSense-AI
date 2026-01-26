import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import '../styles/RiskAssessment.css';

const RiskAssessment = () => {
  const [selectedTime, setSelectedTime] = useState('less-than-30');
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [riskLevel, setRiskLevel] = useState({ level: 'LOW', message: 'Monitor symptoms. Contact healthcare provider if condition worsens.' });

  const timeOptions = [
    { id: 'less-than-30', label: 'Less than 30 min' },
    { id: '30-60', label: '30-60 minutes' },
    { id: '1-2-hours', label: '1-2 hours' },
    { id: 'more-than-2', label: 'More than 2 hours' }
  ];

  const symptoms = [
    { id: 'nausea', label: 'Nausea or vomiting', severity: 'MODERATE' },
    { id: 'breathing', label: 'Difficulty breathing', severity: 'CRITICAL' },
    { id: 'chest-pain', label: 'Chest pain', severity: 'CRITICAL' },
    { id: 'confusion', label: 'Confusion or disorientation', severity: 'HIGH' },
    { id: 'seizures', label: 'Seizures or convulsions', severity: 'CRITICAL' },
    { id: 'unconscious', label: 'Loss of consciousness', severity: 'CRITICAL' },
    { id: 'abdominal', label: 'Severe abdominal pain', severity: 'HIGH' },
    { id: 'dizziness', label: 'Dizziness or lightheadedness', severity: 'MODERATE' },
    { id: 'skin-rash', label: 'Skin rash or burns', severity: 'MODERATE' },
    { id: 'heartbeat', label: 'Rapid or irregular heartbeat', severity: 'HIGH' },
    { id: 'sweating', label: 'Excessive sweating', severity: 'LOW' },
    { id: 'headache', label: 'Headache', severity: 'LOW' }
  ];

  const getSeverityClass = (severity) => {
    switch (severity) {
      case 'CRITICAL': return 'severity-critical';
      case 'HIGH': return 'severity-high';
      case 'MODERATE': return 'severity-moderate';
      case 'LOW': return 'severity-low';
      default: return '';
    }
  };

  const handleSymptomChange = (symptomId) => {
    setSelectedSymptoms(prev => 
      prev.includes(symptomId) 
        ? prev.filter(id => id !== symptomId)
        : [...prev, symptomId]
    );
  };

  useEffect(() => {
    // Calculate risk level based on selected symptoms
    const selectedSymptomData = symptoms.filter(s => selectedSymptoms.includes(s.id));
    const hasCritical = selectedSymptomData.some(s => s.severity === 'CRITICAL');
    const hasHigh = selectedSymptomData.some(s => s.severity === 'HIGH');
    const hasModerate = selectedSymptomData.some(s => s.severity === 'MODERATE');
    const criticalCount = selectedSymptomData.filter(s => s.severity === 'CRITICAL').length;
    const highCount = selectedSymptomData.filter(s => s.severity === 'HIGH').length;

    if (hasCritical || criticalCount >= 1) {
      setRiskLevel({
        level: 'CRITICAL',
        message: 'EMERGENCY! Call 102 immediately. Life-threatening symptoms detected.'
      });
    } else if (highCount >= 2 || (hasHigh && hasModerate)) {
      setRiskLevel({
        level: 'HIGH',
        message: 'Seek immediate medical attention. Multiple concerning symptoms present.'
      });
    } else if (hasHigh || hasModerate) {
      setRiskLevel({
        level: 'MODERATE',
        message: 'Contact healthcare provider soon. Monitor symptoms closely.'
      });
    } else {
      setRiskLevel({
        level: 'LOW',
        message: 'Monitor symptoms. Contact healthcare provider if condition worsens.'
      });
    }
  }, [selectedSymptoms]);

  const getRiskClass = () => {
    switch (riskLevel.level) {
      case 'CRITICAL': return 'risk-critical';
      case 'HIGH': return 'risk-high';
      case 'MODERATE': return 'risk-moderate';
      case 'LOW': return 'risk-low';
      default: return 'risk-low';
    }
  };

  return (
    <div className="risk-page">
      {/* Navigation */}
      <Navbar />

      {/* Main Content */}
      <main className="risk-content">
        <div className="content-container">
          {/* Header */}
          <div className="page-header">
            <h1>Risk Assessment</h1>
            <p>Select all symptoms currently present to assess the risk level</p>
          </div>

          {/* White Card Container for Disclaimer and Risk */}
          <div className="risk-card-container">
            {/* Medical Disclaimer */}
            <div className="disclaimer-box">
              <div className="disclaimer-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="#D97706">
                  <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
                </svg>
              </div>
              <p>Medical Disclaimer: This system does not replace professional medical care. In emergencies, contact local emergency services immediately.</p>
            </div>

            {/* Risk Level Display */}
            <div className={`risk-display ${getRiskClass()}`}>
              <div className="risk-icon">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </div>
              <div className="risk-info">
                <h2>{riskLevel.level} RISK</h2>
                <p>{riskLevel.message}</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Assessment Card Section - White Background */}
      <section className="assessment-section">
        <div className="assessment-section-container">
          {/* Assessment Card */}
          <div className="assessment-card">
            {/* Time Since Exposure */}
            <div className="time-section">
              <h3>Time Since Exposure</h3>
              <div className="time-options">
                {timeOptions.map(option => (
                  <button
                    key={option.id}
                    className={`time-btn ${selectedTime === option.id ? 'active' : ''}`}
                    onClick={() => setSelectedTime(option.id)}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Symptoms Checklist */}
            <div className="symptoms-section">
              <h3>Current Symptoms</h3>
              <div className="symptoms-list">
                {symptoms.map(symptom => (
                  <label key={symptom.id} className="symptom-item">
                    <input
                      type="checkbox"
                      checked={selectedSymptoms.includes(symptom.id)}
                      onChange={() => handleSymptomChange(symptom.id)}
                    />
                    <span className="checkbox-custom"></span>
                    <span className="symptom-label">{symptom.label}</span>
                    <span className={`severity-badge ${getSeverityClass(symptom.severity)}`}>
                      {symptom.severity}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="action-buttons">
              <button className="btn-guidance">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
                  <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                </svg>
                View Emergency Guidance
              </button>
              <button className="btn-find-help">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
                  <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                </svg>
                Find Nearby Help
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-container">
          <h2>Ready to Get Help?</h2>
          <p>Start your AI assessment now or contact emergency services immediately if you're in a critical situation</p>
          <div className="cta-buttons">
            <Link to="/assessment" className="btn-emergency">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-1 11h-4v4h-4v-4H6v-4h4V6h4v4h4v4z"/>
              </svg>
              Start Emergency Assessment
            </Link>
            <a href="tel:100" className="btn-call">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
              </svg>
              Call 102 Now
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <Footer />

      {/* Floating Call Button */}
      <a href="tel:102" className="floating-call-btn">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="white">
          <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
        </svg>
      </a>
    </div>
  );
};

export default RiskAssessment;
