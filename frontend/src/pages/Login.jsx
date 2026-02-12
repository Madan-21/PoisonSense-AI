import React, { useState, useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getErrorMessage } from "../utils/errorHandler";

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
// Login page
export default function Login() {
  const [remember, setRemember] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [email, setEmail] = useState("");
  const [emailError, setEmailError] = useState(null);
  const [showVerification, setShowVerification] = useState(false);
  const [devModeOTP, setDevModeOTP] = useState(null);
  const { login, pendingVerification, verifyOTP, resendOTP } = useAuth();
  const navigate = useNavigate();
  
  // Real-time email validation
  const emailValidation = useMemo(() => validateEmail(email), [email]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setEmailError(null);
    
    // Validate email before submission
    if (!emailValidation.valid) {
      setEmailError(emailValidation.error);
      return;
    }
    
    setIsLoading(true);

    // Collect form values
    const formData = new FormData(e.currentTarget);
    const password = formData.get("password");

    try {
      await login(email.toLowerCase(), password);
      navigate("/"); // Redirect to home on success
    } catch (err) {
      const errorMsg = getErrorMessage(err, "Login failed. Please check your credentials.");
      
      // Check if email verification is required
      if (errorMsg.includes('not verified') || errorMsg.includes('verification')) {
        // Check if DEV_MODE OTP is included
        if (errorMsg.includes('DEV_MODE')) {
          const otpMatch = errorMsg.match(/DEV_MODE: Your OTP is (\d{6})/);
          if (otpMatch) {
            setDevModeOTP(otpMatch[1]);
          }
        }
        setShowVerification(true);
        setError("Please verify your email to continue. A verification code has been sent.");
      } else if (errorMsg.includes('email') || errorMsg.includes('Email')) {
        setEmailError(errorMsg);
      } else {
        setError(errorMsg);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Handle OTP verification from login page
  const handleVerificationSuccess = (response) => {
    navigate("/");
  };

  // If showing verification (user tried to login but email not verified)
  if (showVerification && email) {
    // Dynamically import OTPVerification
    const OTPVerification = React.lazy(() => import('../components/OTPVerification'));
    
    return (
      <div className="auth-body">
        <div className="auth-container">
          <div className="auth-header">
            <img src="/images/logo.jpg" alt="PoisonSense AI" />
            <h2>PoisonSense AI</h2>
          </div>
          <React.Suspense fallback={<div>Loading...</div>}>
            <OTPVerification 
              email={email}
              onVerified={handleVerificationSuccess}
              onBack={() => setShowVerification(false)}
              devModeOTP={devModeOTP}
            />
          </React.Suspense>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-body">
      <div className="auth-container">
        {/* Logo / Header */}
        <div className="auth-header">
          {/* Logo with shield icon */}
          <div className="logo-circle">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="white">
              <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>
            </svg>
          </div>
          <h2>PoisonSense AI</h2>
          <h3>Welcome Back</h3>
          <p>Sign in to access emergency support</p>
        </div>

        {/* Login Form */}
        <form className="auth-form" onSubmit={handleSubmit}>
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
          
          <label>Email Address</label>
          <div className="input-box" style={{ borderColor: emailError ? '#dc3545' : (email && emailValidation.valid ? '#28a745' : '') }}>
            <input
              type="email"
              name="email"
              placeholder="your.email@example.com"
              required
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                setEmailError(null);
              }}
            />
          </div>
          {emailError && (
            <p style={{ color: '#dc3545', fontSize: '12px', marginTop: '4px', marginBottom: '10px' }}>
              ⚠️ {emailError}
            </p>
          )}
          {email && !emailValidation.valid && !emailError && (
            <p style={{ color: '#dc3545', fontSize: '12px', marginTop: '4px', marginBottom: '10px' }}>
              ⚠️ {emailValidation.error}
            </p>
          )}

          <label>Password</label>
          <div className="input-box">
            <input
              type="password"
              name="password"
              placeholder="Enter your password"
              required
            />
          </div>

          <div className="auth-row">
            <label className="remember">
              <input
                type="checkbox"
                name="remember"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
              />
              <span>Remember me</span>
            </label>

            {/* If you have forgot password page, change route */}
            <Link to="/forgot-password" className="forgot-link">
              Forgot Password?
            </Link>
          </div>

          <button type="submit" className="btn-primary" disabled={isLoading}>
            {isLoading ? "⏳ Signing In..." : "➡️ Sign In"}
          </button>

          <div className="auth-footer-text">
            Don’t have an account? <Link to="/signup">Sign Up</Link>
          </div>
        </form>

        {/* Emergency Box */}
        <div className="emergency-box"> 
          <h4>⚠ Emergency Situation?</h4>
          <p>You can access emergency features without logging in.</p>
          <Link to="/findhelp" className="btn-emergency">
            Get Emergency Help Now
          </Link>
        </div>
      </div>
    </div>
  );
}
