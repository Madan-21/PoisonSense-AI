import React, { useMemo, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import OTPVerification from "../components/OTPVerification";

// Valid TLDs for email validation
const VALID_TLDS = new Set([
  'com', 'org', 'net', 'edu', 'gov', 'io', 'co', 'in', 'np', 'uk',
  'us', 'ca', 'au', 'de', 'fr', 'jp', 'cn', 'ru', 'br', 'mx',
  'info', 'biz', 'me', 'tv', 'app', 'dev', 'tech', 'online',
  'store', 'shop', 'site', 'xyz', 'ai'
]);

// Common email domain typos
const COMMON_TYPOS = {
  'gmial.com': 'gmail.com',
  'gmal.com': 'gmail.com',
  'gamil.com': 'gmail.com',
  'gmail.comm': 'gmail.com',
  'gmail.con': 'gmail.com',
  'gmail.co': 'gmail.com',
  'yahooo.com': 'yahoo.com',
  'yahoo.comm': 'yahoo.com',
  'yahoo.con': 'yahoo.com',
  'hotmal.com': 'hotmail.com',
  'hotmail.comm': 'hotmail.com',
  'hotmail.con': 'hotmail.com',
  'outlok.com': 'outlook.com',
  'outlook.comm': 'outlook.com',
};

// Validate email domain
const validateEmail = (email) => {
  if (!email || !email.includes('@')) {
    return { valid: false, error: 'Please enter a valid email address' };
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return { valid: false, error: 'Please enter a valid email address' };
  }
  
  const domain = email.split('@')[1].toLowerCase();
  const parts = domain.split('.');
  
  if (parts.length < 2) {
    return { valid: false, error: 'Invalid email domain' };
  }
  
  const tld = parts[parts.length - 1];
  
  // Check for common typos
  if (COMMON_TYPOS[domain]) {
    return { valid: false, error: `Did you mean ${email.split('@')[0]}@${COMMON_TYPOS[domain]}?` };
  }
  
  // Check for valid TLD
  if (!VALID_TLDS.has(tld)) {
    return { valid: false, error: `Invalid email domain extension ".${tld}"` };
  }
  
  return { valid: true, error: null };
};

// Validate password strength
const validatePassword = (password) => {
  const errors = [];
  
  if (password.length < 8) {
    errors.push('At least 8 characters');
  }
  if (!/[A-Z]/.test(password)) {
    errors.push('One uppercase letter');
  }
  if (!/[a-z]/.test(password)) {
    errors.push('One lowercase letter');
  }
  if (!/\d/.test(password)) {
    errors.push('One number');
  }
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('One special character (!@#$%^&*(),.?":{}|<>)');
  }
  
  return {
    valid: errors.length === 0,
    errors,
    strength: errors.length === 0 ? 'strong' : errors.length <= 2 ? 'medium' : 'weak'
  };
};

// Validate phone number
const validatePhone = (phone) => {
  if (!phone) return { valid: true, error: null }; // Optional field
  
  const cleaned = phone.replace(/[\s\-]/g, '');
  const phoneRegex = /^\+?\d{10,15}$/;
  
  if (!phoneRegex.test(cleaned)) {
    return { valid: false, error: 'Phone must be 10-15 digits (optionally starting with +)' };
  }
  
  return { valid: true, error: null };
};

export default function Signup() {
  const [role, setRole] = useState("");
  const [pass, setPass] = useState("");
  const [confirmPass, setConfirmPass] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});
  const [showOTPVerification, setShowOTPVerification] = useState(false);
  const [verificationEmail, setVerificationEmail] = useState("");
  const [devModeOTP, setDevModeOTP] = useState(null);
  
  const { signup, pendingVerification } = useAuth();
  const navigate = useNavigate();

  const passwordsMatch = useMemo(() => pass === confirmPass, [pass, confirmPass]);
  const showPassError = useMemo(
    () => (pass.length > 0 || confirmPass.length > 0) && !passwordsMatch,
    [pass, confirmPass, passwordsMatch]
  );
  
  // Real-time validation
  const emailValidation = useMemo(() => validateEmail(email), [email]);
  const passwordValidation = useMemo(() => validatePassword(pass), [pass]);
  const phoneValidation = useMemo(() => validatePhone(phone), [phone]);

  const isDoctor = role === "doctor";
  const isHospital = role === "hospital";

  // ✅ Dynamic label + placeholder based on role
  const nameLabel = isDoctor
    ? "Doctor Full Name *"
    : isHospital
    ? "Hospital / Organization Name *"
    : "Full Name / Organization Name *";

  const namePlaceholder = isDoctor
    ? "Enter doctor full name"
    : isHospital
    ? "Enter hospital name"
    : "Your name or hospital name";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setFieldErrors({});

    // Validation
    const errors = {};

    if (!role) {
      setError("Please select an account type.");
      return;
    }
    
    // Email validation
    if (!emailValidation.valid) {
      errors.email = emailValidation.error;
    }
    
    // Password validation
    if (!passwordValidation.valid) {
      errors.password = `Password needs: ${passwordValidation.errors.join(', ')}`;
    }
    
    // Password match
    if (!passwordsMatch) {
      errors.confirmPassword = "Passwords do not match";
    }
    
    // Phone validation
    if (!phoneValidation.valid) {
      errors.phone = phoneValidation.error;
    }
    
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      setError("Please fix the errors below.");
      return;
    }

    setIsLoading(true);
    const form = e.currentTarget;
    const formData = new FormData(form);

    try {
      const userData = {
        email: email.toLowerCase(),
        password: pass,
        full_name: formData.get("full_name"),
        phone: phone || null,
      };
      
      const response = await signup(userData);
      
      // Show OTP verification screen
      if (response.requires_verification) {
        setVerificationEmail(response.email);
        
        // Check if DEV_MODE OTP is returned (when email service isn't configured)
        if (response.message && response.message.includes("DEV_MODE")) {
          const otpMatch = response.message.match(/DEV_MODE: Your OTP is (\d{6})/);
          if (otpMatch) {
            setDevModeOTP(otpMatch[1]);
          }
        }
        
        setShowOTPVerification(true);
      } else {
        setSuccess(true);
        setTimeout(() => navigate("/"), 2000);
      }
    } catch (err) {
      // Parse validation errors from backend
      const errorMsg = err.response?.data?.detail || err.message || "Registration failed. Please try again.";
      if (errorMsg.includes('email') || errorMsg.includes('Email')) {
        setFieldErrors(prev => ({ ...prev, email: errorMsg }));
      } else if (errorMsg.includes('password') || errorMsg.includes('Password')) {
        setFieldErrors(prev => ({ ...prev, password: errorMsg }));
      } else {
        setError(errorMsg);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Handle OTP verification success
  const handleVerificationSuccess = (response) => {
    setSuccess(true);
    // Redirect to home after successful verification
    setTimeout(() => {
      navigate("/");
    }, 1500);
  };

  // Handle back from OTP verification
  const handleBackFromOTP = () => {
    setShowOTPVerification(false);
    setVerificationEmail("");
  };

  // If showing OTP verification
  if (showOTPVerification) {
    return (
      <div className="auth-body">
        <div className="auth-container">
          <div className="auth-header">
            <img src="/images/logo.jpg" alt="PoisonSense AI" />
            <h2>PoisonSense AI</h2>
          </div>
          <OTPVerification 
            email={verificationEmail}
            onVerified={handleVerificationSuccess}
            onBack={handleBackFromOTP}
            devModeOTP={devModeOTP}
          />
        </div>
      </div>
    );
  }

  // Password strength indicator
  const getPasswordStrengthColor = () => {
    if (pass.length === 0) return '#ddd';
    switch (passwordValidation.strength) {
      case 'strong': return '#28a745';
      case 'medium': return '#ffc107';
      default: return '#dc3545';
    }
  };

  return (
    <div className="auth-body">
      <div className="auth-container">
        {/* Header */}
        <div className="auth-header">
          <img src="/images/logo.jpg" alt="PoisonSense AI" />
          <h2>PoisonSense AI</h2>
          <h3>Create Your Account</h3>
          <p>Join us to access life-saving emergency support</p>
        </div>

        {/* Form */}
        <form
          className="auth-form"
          id="signupForm"
          onSubmit={handleSubmit}
          encType="multipart/form-data"
        >
          {error && (
            <div className="error-message" style={{ 
              color: '#dc3545', 
              backgroundColor: '#f8d7da', 
              padding: '10px', 
              borderRadius: '8px', 
              marginBottom: '15px',
              fontSize: '14px'
            }}>
              ⚠️ {error}
            </div>
          )}
          
          {success && (
            <div className="success-message" style={{ 
              color: '#155724', 
              backgroundColor: '#d4edda', 
              padding: '10px', 
              borderRadius: '8px', 
              marginBottom: '15px',
              fontSize: '14px'
            }}>
              ✅ Account created successfully! Redirecting to login...
            </div>
          )}
          
          {/* ROLE */}
          <label>Account Type *</label>
          <div className="input-box">
            <select
              id="roleSelect"
              name="role"
              required
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              <option value="">Select account type</option>
              <option value="doctor">Doctor</option>
              <option value="hospital">Hospital</option>
            </select>
          </div>

          {/* ✅ Dynamic Full Name / Hospital Name */}
          <label>{nameLabel}</label>
          <div className="input-box">
            <input
              type="text"
              name="full_name"
              placeholder={namePlaceholder}
              required
              minLength={2}
              maxLength={255}
            />
          </div>

          <div className="input-row">
            <div>
              <label>Email Address *</label>
              <div className="input-box" style={{ borderColor: fieldErrors.email ? '#dc3545' : (email && emailValidation.valid ? '#28a745' : '') }}>
                <input
                  type="email"
                  name="email"
                  placeholder="your.email@example.com"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              {fieldErrors.email && (
                <p style={{ color: '#dc3545', fontSize: '12px', marginTop: '4px' }}>
                  ⚠️ {fieldErrors.email}
                </p>
              )}
              {email && !emailValidation.valid && !fieldErrors.email && (
                <p style={{ color: '#dc3545', fontSize: '12px', marginTop: '4px' }}>
                  ⚠️ {emailValidation.error}
                </p>
              )}
            </div>

            <div>
              <label>Phone Number</label>
              <div className="input-box" style={{ borderColor: fieldErrors.phone ? '#dc3545' : (phone && phoneValidation.valid ? '#28a745' : '') }}>
                <input 
                  type="tel" 
                  name="phone" 
                  placeholder="+977-98XXXXXXXX" 
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                />
              </div>
              {fieldErrors.phone && (
                <p style={{ color: '#dc3545', fontSize: '12px', marginTop: '4px' }}>
                  ⚠️ {fieldErrors.phone}
                </p>
              )}
            </div>
          </div>

          <div className="input-row">
            <div>
              <label>Password *</label>
              <div className="input-box" style={{ borderColor: fieldErrors.password ? '#dc3545' : (pass && passwordValidation.valid ? '#28a745' : '') }}>
                <input
                  type="password"
                  id="password"
                  name="password"
                  placeholder="Create password"
                  required
                  value={pass}
                  onChange={(e) => setPass(e.target.value)}
                />
              </div>
              {/* Password strength indicator */}
              {pass.length > 0 && (
                <div style={{ marginTop: '4px' }}>
                  <div style={{ 
                    height: '4px', 
                    backgroundColor: '#ddd', 
                    borderRadius: '2px',
                    overflow: 'hidden'
                  }}>
                    <div style={{ 
                      height: '100%', 
                      width: passwordValidation.strength === 'strong' ? '100%' : passwordValidation.strength === 'medium' ? '60%' : '30%',
                      backgroundColor: getPasswordStrengthColor(),
                      transition: 'all 0.3s'
                    }} />
                  </div>
                  <p style={{ 
                    fontSize: '11px', 
                    color: getPasswordStrengthColor(), 
                    marginTop: '2px' 
                  }}>
                    {passwordValidation.valid ? '✅ Strong password' : `Needs: ${passwordValidation.errors.join(', ')}`}
                  </p>
                </div>
              )}
              {fieldErrors.password && (
                <p style={{ color: '#dc3545', fontSize: '12px', marginTop: '4px' }}>
                  ⚠️ {fieldErrors.password}
                </p>
              )}
            </div>

            <div>
              <label>Confirm Password *</label>
              <div className="input-box" style={{ borderColor: confirmPass && !passwordsMatch ? '#dc3545' : (confirmPass && passwordsMatch ? '#28a745' : '') }}>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirm_password"
                  placeholder="Confirm password"
                  required
                  value={confirmPass}
                  onChange={(e) => setConfirmPass(e.target.value)}
                />
              </div>
              {fieldErrors.confirmPassword && (
                <p style={{ color: '#dc3545', fontSize: '12px', marginTop: '4px' }}>
                  ⚠️ {fieldErrors.confirmPassword}
                </p>
              )}
            </div>
          </div>

          {/* Password error */}
          <p
            id="passError"
            style={{
              display: showPassError ? "block" : "none",
              marginTop: "-8px",
              fontSize: "13px",
              color: "#ff5b5b",
            }}
          >
            ⚠ Passwords do not match.
          </p>

          {/* DOCTOR EXTRA (no consultation mode) */}
          <div id="doctorFields" style={{ display: isDoctor ? "block" : "none" }}>
            <div className="input-row">
              <div>
                <label>Medical Registration No. *</label>
                <div className="input-box">
                  <input
                    type="text"
                    name="doctor_reg_no"
                    placeholder="e.g., NMC-XXXXX"
                    disabled={!isDoctor}
                    required={isDoctor}
                  />
                </div>
              </div>

              <div>
                <label>Poison-related Specialization *</label>
                <div className="input-box">
                  <select
                    name="doctor_specialization"
                    disabled={!isDoctor}
                    required={isDoctor}
                    defaultValue=""
                  >
                    <option value="">Select specialization</option>
                    <option>Clinical Toxicology</option>
                    <option>Emergency Medicine (Poisoning & Overdose)</option>
                    <option>Internal Medicine (Toxicology Focus)</option>
                    <option>Pediatrics (Poisoning Cases)</option>
                    <option>Pharmacology / Poison Information</option>
                    <option>ICU / Critical Care (Toxic Exposure)</option>
                    <option>Occupational & Environmental Medicine</option>
                    <option>Forensic Medicine (Poisoning/Overdose)</option>
                    <option>Other (Poison-related)</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="input-row">
              <div>
                <label>Experience (Years)</label>
                <div className="input-box">
                  <input
                    type="number"
                    name="doctor_experience"
                    min="0"
                    placeholder="e.g., 5"
                    disabled={!isDoctor}
                  />
                </div>
              </div>
            </div>

            <label>Upload Medical License (PDF/JPG) *</label>
            <div className="input-box">
              <input
                type="file"
                name="doctor_license"
                accept=".pdf,.jpg,.jpeg,.png"
                disabled={!isDoctor}
                required={isDoctor}
              />
            </div>
          </div>

          {/* HOSPITAL EXTRA (no consultation mode) */}
          <div id="hospitalFields" style={{ display: isHospital ? "block" : "none" }}>
            <div className="input-row">
              <div>
                <label>Hospital Registration No. *</label>
                <div className="input-box">
                  <input
                    type="text"
                    name="hospital_reg_no"
                    placeholder="Enter registration number"
                    disabled={!isHospital}
                    required={isHospital}
                  />
                </div>
              </div>

              <div>
                <label>Poison-related Department *</label>
                <div className="input-box">
                  <select
                    name="hospital_department"
                    disabled={!isHospital}
                    required={isHospital}
                    defaultValue=""
                  >
                    <option value="">Select department</option>
                    <option>Toxicology / Poison Unit</option>
                    <option>Emergency (Poison Cases)</option>
                    <option>ICU (Toxic Exposure)</option>
                    <option>Pharmacology / Poison Info Center</option>
                    <option>Pediatrics (Poisoning)</option>
                    <option>Occupational & Environmental Medicine</option>
                    <option>Forensic Medicine (Poisoning)</option>
                    <option>Other (Poison-related)</option>
                  </select>
                </div>
              </div>
            </div>

            <label>Address *</label>
            <div className="input-box">
              <input
                type="text"
                name="hospital_address"
                placeholder="Hospital address"
                disabled={!isHospital}
                required={isHospital}
              />
            </div>

            <label>Upload Hospital License (PDF/JPG) *</label>
            <div className="input-box">
              <input
                type="file"
                name="hospital_license"
                accept=".pdf,.jpg,.jpeg,.png"
                disabled={!isHospital}
                required={isHospital}
              />
            </div>

            <div className="input-row">
              <div>
                <label>Emergency Service *</label>
                <div className="input-box">
                  <select
                    name="hospital_emergency"
                    disabled={!isHospital}
                    required={isHospital}
                    defaultValue=""
                  >
                    <option value="">Select</option>
                    <option>Yes</option>
                    <option>No</option>
                  </select>
                </div>
              </div>
            </div>

            <label>Operating Hours</label>
            <div className="input-box">
              <input
                type="text"
                name="hospital_hours"
                placeholder="e.g., 24/7 or 9AM - 6PM"
                disabled={!isHospital}
              />
            </div>
          </div>

          {/* Terms */}
          <div className="checkbox">
            <input type="checkbox" name="terms" required />
            <span>
              I agree to the <a href="#">Terms of Service</a> and{" "}
              <a href="#">Privacy Policy</a>
            </span>
          </div>

          <button type="submit" className="btn-primary" disabled={isLoading || success}>
            {isLoading ? "⏳ Creating Account..." : "👤 Create Account"}
          </button>
        </form>

        {/* Emergency Box */}
        <div className="emergency-box">
          <h4>⚠ Emergency Situation?</h4>
          <p>You can access emergency features without creating an account.</p>
          <a href="/findhelp" className="btn-emergency">
            Get Emergency Help Now
          </a>
        </div>
      </div>
    </div>
  );
}
