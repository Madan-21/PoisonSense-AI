import React, { useState, useMemo } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getErrorMessage } from "../utils/errorHandler";
import asset from "../utils/asset";
import "../styles/Login.css";

/* Valid TLDs for email validation */
const VALID_TLDS = new Set([
  "com", "org", "net", "edu", "gov", "io", "co", "in", "np", "uk",
  "us", "ca", "au", "de", "fr", "jp", "cn", "ru", "br", "mx",
  "info", "biz", "me", "tv", "app", "dev", "tech", "online",
  "store", "shop", "site", "xyz", "ai",
]);

/* Common email domain typos */
const COMMON_TYPOS = {
  "gmial.com": "gmail.com",
  "gmal.com": "gmail.com",
  "gamil.com": "gmail.com",
  "gmail.comm": "gmail.com",
  "gmail.con": "gmail.com",
  "gmail.co": "gmail.com",
  "yahooo.com": "yahoo.com",
  "yahoo.comm": "yahoo.com",
  "yahoo.con": "yahoo.com",
  "hotmal.com": "hotmail.com",
  "hotmail.comm": "hotmail.com",
  "hotmail.con": "hotmail.com",
  "outlok.com": "outlook.com",
  "outlook.comm": "outlook.com",
};

/* Validate email domain */
const validateEmail = (email) => {
  if (!email || !email.includes("@")) {
    return { valid: false, error: "Please enter a valid email address" };
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return { valid: false, error: "Please enter a valid email address" };
  }

  const domain = email.split("@")[1].toLowerCase();
  const parts = domain.split(".");
  if (parts.length < 2) return { valid: false, error: "Invalid email domain" };

  const tld = parts[parts.length - 1];

  if (COMMON_TYPOS[domain]) {
    return {
      valid: false,
      error: `Did you mean ${email.split("@")[0]}@${COMMON_TYPOS[domain]}?`,
    };
  }

  if (!VALID_TLDS.has(tld)) {
    return { valid: false, error: `Invalid email domain extension ".${tld}"` };
  }

  return { valid: true, error: null };
};

export default function Login() {
  const [remember, setRemember] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const [error, setError] = useState(null);
  const [email, setEmail] = useState("");
  const [emailError, setEmailError] = useState(null);
  const [infoMessage, setInfoMessage] = useState(null);

  const [showVerification, setShowVerification] = useState(false);
  const [devModeOTP, setDevModeOTP] = useState(null);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const emailValidation = useMemo(() => validateEmail(email), [email]);

  // Get the page user was trying to access before being redirected to login
  // Only redirect back if they were sent here by ProtectedRoute (has from state)
  // Otherwise always go to Home after login
  const from = location.state?.from?.pathname || "/";
  
  // Check for info message from signup/verification
  React.useEffect(() => {
    if (location.state?.message) {
      setInfoMessage(location.state.message);
      // Clear the message from location state
      window.history.replaceState({}, document.title);
    }
  }, [location]);

  /** ✅ Navigate to intended destination or home */
  const goHome = () => {
    navigate("/", { replace: true });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setEmailError(null);

    if (!emailValidation.valid) {
      setEmailError(emailValidation.error);
      return;
    }

    setIsLoading(true);

    const formData = new FormData(e.currentTarget);
    const password = formData.get("password");

    try {
      await login(email.toLowerCase(), password);
      // Always go to Home after successful login
      navigate("/", { replace: true });
    } catch (err) {
      const errorMsg = getErrorMessage(err, "Login failed. Please check your credentials.");

      // Check for pending admin approval FIRST (before checking verification)
      if (errorMsg.includes("pending admin approval") || errorMsg.includes("pending approval")) {
        setError(null);
        setInfoMessage("⏳ Your account is pending admin approval. Please wait 24-48 hours. You will receive an email notification once approved.");
      } else if (errorMsg.includes("not verified") || (errorMsg.includes("verification") && errorMsg.includes("code"))) {
        if (errorMsg.includes("DEV_MODE")) {
          const otpMatch = errorMsg.match(/DEV_MODE: Your OTP is (\d{6})/);
          if (otpMatch) setDevModeOTP(otpMatch[1]);
        }
        setShowVerification(true);
        setError("Please verify your email to continue. A verification code has been sent.");
      } else if (errorMsg.toLowerCase().includes("email")) {
        setEmailError(errorMsg);
      } else {
        setError(errorMsg);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerificationSuccess = () => {
    // Redirect to the page user was trying to access, or home
    navigate(from, { replace: true });
  };

  // OTP Screen
  if (showVerification && email) {
    const OTPVerification = React.lazy(() => import("../components/OTPVerification"));

    return (
      <div className="login-split-page">
        <div className="login-split-card only-right">
          <div className="login-right">
            {/* ✅ Back button always goes home */}
            <button type="button" className="back-home" onClick={goHome}>
              ← Back to Home
            </button>

            <div className="brand-row">
              <img className="brand-logo-img" src={asset("/images/logo.jpg")} alt="PoisonSense Logo" />
              <div className="brand-text">
                <div className="brand-title">PoisonSense AI</div>
                <div className="brand-sub">Email Verification</div>
              </div>
            </div>

            {error && <div className="alert error">{error}</div>}

            <React.Suspense fallback={<div className="loading">Loading...</div>}>
              <OTPVerification
                email={email}
                onVerified={handleVerificationSuccess}
                onBack={() => setShowVerification(false)}
                devModeOTP={devModeOTP}
              />
            </React.Suspense>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="login-split-page">
      <div className="login-split-card">
        {/* LEFT IMAGE PANEL */}
        <div className="login-left">
          <img className="left-bg-img" src={asset("/images/poisonss.jpg")} alt="PoisonSense Banner" />
          <div className="left-overlay">
            <div className="left-badge">
              <span className="dot" />
              Emergency-ready support
            </div>

            <h2 className="left-title">Fast poison guidance</h2>
            <p className="left-desc">
              Save allergies, conditions & contacts so PoisonSense AI can help faster during emergencies.
            </p>

            <div className="left-points">
              <div className="point">✅ Smart emergency guidance</div>
              <div className="point">✅ Quick contact notification</div>
              <div className="point">✅ Secure profile storage</div>
            </div>
          </div>
        </div>

        {/* RIGHT LOGIN PANEL */}
        <div className="login-right">
          {/* ✅ Back button always goes home */}
          <button type="button" className="back-home" onClick={goHome}>
            ← Back to Home
          </button>

          <div className="brand-row">
            <img className="brand-logo-img" src={asset("/images/logo.jpg")} alt="PoisonSense Logo" />
            <div className="brand-text">
              <div className="brand-title">PoisonSense AI</div>
              <div className="brand-sub">Sign in to continue</div>
            </div>
          </div>

          <form className="login-form" onSubmit={handleSubmit}>
            {infoMessage && <div className="alert info" style={{backgroundColor: '#e8f5e9', color: '#2e7d32', border: '1px solid #4caf50'}}>ℹ️ {infoMessage}</div>}
            {error && <div className="alert error">⚠️ {error}</div>}

            <label className="label">Email Address</label>
            <div
              className={`input-wrap ${
                emailError
                  ? "error-border"
                  : email && emailValidation.valid
                  ? "success-border"
                  : ""
              }`}
            >
              <input
                type="email"
                name="email"
                placeholder="you@example.com"
                required
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setEmailError(null);
                }}
              />
            </div>

            {emailError && <p className="mini-error">⚠️ {emailError}</p>}
            {email && !emailValidation.valid && !emailError && (
              <p className="mini-error">⚠️ {emailValidation.error}</p>
            )}

            <label className="label">Password</label>
            <div className="input-wrap">
              <input type="password" name="password" placeholder="Enter password" required />
            </div>

            <div className="row">
              <label className="remember">
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                />
                <span>Remember me</span>
              </label>

              <Link to="/forgot-password" className="forgot">
                Forgot password?
              </Link>
            </div>

            <button type="submit" className="btn-main" disabled={isLoading}>
              {isLoading ? "⏳ Signing In..." : "Sign In"}
            </button>

            <div className="signup-text">
              Don’t have an account? <Link to="/signup">Sign up</Link>
            </div>

            <div className="emergency-box">
              <div className="em-title">⚠ Emergency Situation?</div>
              <div className="em-desc">
                You can access emergency features without logging in.
              </div>
              <Link to="/find-help" className="btn-emergency">
                Get Emergency Help Now
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}