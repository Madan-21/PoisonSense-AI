import React, { useMemo, useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import OTPVerification from "../components/OTPVerification";
import { getErrorMessage } from "../utils/errorHandler";
import "../styles/signup.css";

// Valid TLDs for email validation
const VALID_TLDS = new Set([
  "com","org","net","edu","gov","io","co","in","np","uk",
  "us","ca","au","de","fr","jp","cn","ru","br","mx",
  "info","biz","me","tv","app","dev","tech","online",
  "store","shop","site","xyz","ai"
]);

// Common email domain typos
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

// Validate email domain
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

// Validate password strength
const validatePassword = (password) => {
  const errors = [];
  if (password.length < 8) errors.push("At least 8 characters");
  if (!/[A-Z]/.test(password)) errors.push("One uppercase letter");
  if (!/[a-z]/.test(password)) errors.push("One lowercase letter");
  if (!/\d/.test(password)) errors.push("One number");
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('One special character (!@#$%^&*(),.?":{}|<>)');
  }

  return {
    valid: errors.length === 0,
    errors,
    strength: errors.length === 0 ? "strong" : errors.length <= 2 ? "medium" : "weak",
  };
};

// Validate phone number
const validatePhone = (phone) => {
  if (!phone) return { valid: true, error: null };

  const cleaned = phone.replace(/[\s\-]/g, "");
  const phoneRegex = /^\+?\d{10,15}$/;

  if (!phoneRegex.test(cleaned)) {
    return { valid: false, error: "Phone must be 10-15 digits (optionally starting with +)" };
  }

  return { valid: true, error: null };
};

export default function Signup() {
  const navigate = useNavigate();
  const { signup } = useAuth();

  const [role, setRole] = useState("");
  const [pass, setPass] = useState("");
  const [confirmPass, setConfirmPass] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");

  // ✅ Profile photo LAST
  const [profilePhoto, setProfilePhoto] = useState(null);
  const [profilePreview, setProfilePreview] = useState("");

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});
  const [showOTPVerification, setShowOTPVerification] = useState(false);
  const [verificationEmail, setVerificationEmail] = useState("");
  const [devModeOTP, setDevModeOTP] = useState(null);

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const passwordsMatch = useMemo(() => pass === confirmPass, [pass, confirmPass]);
  const showPassError = useMemo(
    () => (pass.length > 0 || confirmPass.length > 0) && !passwordsMatch,
    [pass, confirmPass, passwordsMatch]
  );

  const emailValidation = useMemo(() => validateEmail(email), [email]);
  const passwordValidation = useMemo(() => validatePassword(pass), [pass]);
  const phoneValidation = useMemo(() => validatePhone(phone), [phone]);

  const isDoctor = role === "doctor";
  const isHospital = role === "hospital";

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

  useEffect(() => {
    if (!profilePhoto) {
      setProfilePreview("");
      return;
    }
    const url = URL.createObjectURL(profilePhoto);
    setProfilePreview(url);
    return () => URL.revokeObjectURL(url);
  }, [profilePhoto]);

  const getPasswordStrengthColor = () => {
    if (pass.length === 0) return "#e5e7eb";
    switch (passwordValidation.strength) {
      case "strong": return "#22c55e";
      case "medium": return "#f59e0b";
      default: return "#ef4444";
    }
  };

  const handleVerificationSuccess = () => {
    setSuccess(true);
    setTimeout(() => navigate("/"), 1200);
  };

  const handleBackFromOTP = () => {
    setShowOTPVerification(false);
    setVerificationEmail("");
    setDevModeOTP(null);
  };

  // OTP screen
  if (showOTPVerification) {
    return (
      <div className="signup-page">
        <div className="signup-shell">
          <div className="signup-left">
            <div className="brand-row">
              <img className="brand-logo" src="/images/logo.jpg" alt="PoisonSense AI" />
              <div>
                <div className="brand-name">PoisonSense AI</div>
                <div className="brand-sub">Verify your email</div>
              </div>
            </div>

            <div className="card form-card">
              <OTPVerification
                email={verificationEmail}
                onVerified={handleVerificationSuccess}
                onBack={handleBackFromOTP}
                devModeOTP={devModeOTP}
              />
            </div>
          </div>

          <div className="signup-right" style={{ backgroundImage: "url('/images/Signup.webp')" }}>
            <div className="right-overlay" />
            <div className="right-text">
              <h2>Emergency support, faster</h2>
              <p>Verify once to unlock smart guidance and emergency tools.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setFieldErrors({});

    const errors = {};

    if (!role) {
      setError("Please select an account type.");
      return;
    }

    if (!emailValidation.valid) errors.email = emailValidation.error;

    if (!passwordValidation.valid) {
      errors.password = `Password needs: ${passwordValidation.errors.join(", ")}`;
    }

    if (!passwordsMatch) errors.confirmPassword = "Passwords do not match";

    if (!phoneValidation.valid) errors.phone = phoneValidation.error;

    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      setError("Please fix the errors below.");
      return;
    }

    setIsLoading(true);

    try {
      const formData = new FormData(e.currentTarget);

      formData.set("role", role);
      formData.set("email", email.toLowerCase());
      formData.set("password", pass);
      formData.set("phone", phone || "");

      // ✅ profile photo included only if selected
      if (profilePhoto) formData.set("profile_photo", profilePhoto);

      const response = await signup(formData);

      if (response?.requires_verification) {
        setVerificationEmail(response.email || email.toLowerCase());

        if (response.message && response.message.includes("DEV_MODE")) {
          const otpMatch = response.message.match(/DEV_MODE: Your OTP is (\d{6})/);
          if (otpMatch) setDevModeOTP(otpMatch[1]);
        }

        setShowOTPVerification(true);
      } else {
        setSuccess(true);
        setTimeout(() => navigate("/"), 1500);
      }
    } catch (err) {
      const errorMsg = getErrorMessage(err, "Registration failed. Please try again.");
      if (errorMsg.toLowerCase().includes("email")) {
        setFieldErrors((prev) => ({ ...prev, email: errorMsg }));
      } else if (errorMsg.toLowerCase().includes("password")) {
        setFieldErrors((prev) => ({ ...prev, password: errorMsg }));
      } else {
        setError(errorMsg);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="signup-page">
      <div className="signup-shell">
        {/* LEFT */}
        <div className="signup-left">
          <h1 className="page-title">Create Account</h1>
          <p className="page-subtitle">Sign up to access emergency support & smart assistance.</p>

          <div className="card form-card">
            {error && (
              <div className="alert alert-error">
                <span>⚠️</span>
                <div>{error}</div>
              </div>
            )}

            {success && (
              <div className="alert alert-success">
                <span>✅</span>
                <div>Account created successfully! Redirecting...</div>
              </div>
            )}

            <form className="auth-form" onSubmit={handleSubmit} encType="multipart/form-data">
              {/* ROLE */}
              <div className="field">
                <label className="label">Account Type *</label>
                <select name="role" required value={role} onChange={(e) => setRole(e.target.value)}>
                  <option value="">Select account type</option>
                  <option value="doctor">Doctor</option>
                  <option value="hospital">Hospital</option>
                </select>
              </div>

              {/* NAME */}
              <div className="field">
                <label className="label">{nameLabel}</label>
                <input
                  type="text"
                  name="full_name"
                  placeholder={namePlaceholder}
                  required
                  minLength={2}
                  maxLength={255}
                />
              </div>

              {/* EMAIL + PHONE */}
              <div className="grid-2">
                <div className="field">
                  <label className="label">Email Address *</label>
                  <input
                    type="email"
                    name="email"
                    placeholder="your.email@example.com"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className={fieldErrors.email ? "invalid" : email && emailValidation.valid ? "valid" : ""}
                  />
                  {(fieldErrors.email || (email && !emailValidation.valid)) && (
                    <div className="field-error">⚠️ {fieldErrors.email || emailValidation.error}</div>
                  )}
                </div>

                <div className="field">
                  <label className="label">Phone Number</label>
                  <input
                    type="tel"
                    name="phone"
                    placeholder="+977-98XXXXXXXX"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className={fieldErrors.phone ? "invalid" : phone && phoneValidation.valid ? "valid" : ""}
                  />
                  {fieldErrors.phone && <div className="field-error">⚠️ {fieldErrors.phone}</div>}
                </div>
              </div>

              {/* PASSWORDS */}
              <div className="grid-2">
                <div className="field">
                  <label className="label">Password *</label>
                  <div className="input-with-btn">
                    <input
                      type={showPassword ? "text" : "password"}
                      name="password"
                      placeholder="Create password"
                      required
                      value={pass}
                      onChange={(e) => setPass(e.target.value)}
                      className={fieldErrors.password ? "invalid" : pass && passwordValidation.valid ? "valid" : ""}
                    />
                    <button type="button" className="ghost-btn" onClick={() => setShowPassword((s) => !s)}>
                      {showPassword ? "Hide" : "Show"}
                    </button>
                  </div>

                  {pass.length > 0 && (
                    <div className="strength">
                      <div className="bar">
                        <div
                          className="fill"
                          style={{
                            width:
                              passwordValidation.strength === "strong"
                                ? "100%"
                                : passwordValidation.strength === "medium"
                                ? "60%"
                                : "30%",
                            backgroundColor: getPasswordStrengthColor(),
                          }}
                        />
                      </div>
                      <div className="strength-text" style={{ color: getPasswordStrengthColor() }}>
                        {passwordValidation.valid ? "✅ Strong password" : `Needs: ${passwordValidation.errors.join(", ")}`}
                      </div>
                    </div>
                  )}

                  {fieldErrors.password && <div className="field-error">⚠️ {fieldErrors.password}</div>}
                </div>

                <div className="field">
                  <label className="label">Confirm Password *</label>
                  <div className="input-with-btn">
                    <input
                      type={showConfirmPassword ? "text" : "password"}
                      name="confirm_password"
                      placeholder="Confirm password"
                      required
                      value={confirmPass}
                      onChange={(e) => setConfirmPass(e.target.value)}
                      className={confirmPass && !passwordsMatch ? "invalid" : confirmPass && passwordsMatch ? "valid" : ""}
                    />
                    <button type="button" className="ghost-btn" onClick={() => setShowConfirmPassword((s) => !s)}>
                      {showConfirmPassword ? "Hide" : "Show"}
                    </button>
                  </div>

                  {fieldErrors.confirmPassword && <div className="field-error">⚠️ {fieldErrors.confirmPassword}</div>}
                </div>
              </div>

              {showPassError && <div className="field-error">⚠ Passwords do not match.</div>}

              {/* DOCTOR EXTRA */}
              {isDoctor && (
                <div className="section">
                  <div className="section-title">Doctor Details</div>

                  <div className="grid-2">
                    <div className="field">
                      <label className="label">Medical Registration No. *</label>
                      <input type="text" name="doctor_reg_no" placeholder="e.g., NMC-XXXXX" required />
                    </div>

                    <div className="field">
                      <label className="label">Experience (Years)</label>
                      <input type="number" name="doctor_experience" min="0" placeholder="e.g., 5" />
                    </div>
                  </div>

                  <div className="field">
                    <label className="label">Upload Medical License (PDF/JPG) *</label>
                    <input type="file" name="doctor_license" accept=".pdf,.jpg,.jpeg,.png" required />
                  </div>
                </div>
              )}

              {/* HOSPITAL EXTRA */}
              {isHospital && (
                <div className="section">
                  <div className="section-title">Hospital Details</div>

                  <div className="grid-2">
                    <div className="field">
                      <label className="label">Hospital Registration No. *</label>
                      <input type="text" name="hospital_reg_no" placeholder="Enter registration number" required />
                    </div>

                    <div className="field">
                      <label className="label">Poison-related Department *</label>
                      <select name="hospital_department" required defaultValue="">
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

                  <div className="field">
                    <label className="label">Address *</label>
                    <input type="text" name="hospital_address" placeholder="Hospital address" required />
                  </div>

                  <div className="field">
                    <label className="label">Upload Hospital License (PDF/JPG) *</label>
                    <input type="file" name="hospital_license" accept=".pdf,.jpg,.jpeg,.png" required />
                  </div>

                  <div className="grid-2">
                    <div className="field">
                      <label className="label">Emergency Service *</label>
                      <select name="hospital_emergency" required defaultValue="">
                        <option value="">Select</option>
                        <option>Yes</option>
                        <option>No</option>
                      </select>
                    </div>

                    <div className="field">
                      <label className="label">Operating Hours</label>
                      <input type="text" name="hospital_hours" placeholder="e.g., 24/7 or 9AM - 6PM" />
                    </div>
                  </div>
                </div>
              )}

              {/* ✅ PROFILE PHOTO LAST */}
              <div className="section">
                <div className="section-title">Profile Photo (optional)</div>

                <div className="profile-row">
                  <div className="avatar">
                    {profilePreview ? (
                      <img src={profilePreview} alt="Profile preview" />
                    ) : (
                      <div className="avatar-placeholder">📷</div>
                    )}
                  </div>

                  <div className="profile-actions">
                    <label className="label">Upload photo</label>
                    <input
                      type="file"
                      accept="image/png,image/jpeg,image/jpg"
                      onChange={(e) => {
                        const f = e.target.files?.[0];
                        if (!f) return;
                        setProfilePhoto(f);
                      }}
                    />
                    <div className="helper">PNG/JPG, recommended 400×400</div>

                    {profilePhoto && (
                      <button type="button" className="ghost-btn" onClick={() => setProfilePhoto(null)} style={{ marginTop: 8 }}>
                        Remove photo
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* TERMS */}
              <div className="terms">
                <input type="checkbox" name="terms" required />
                <span>
                  I agree to the <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>
                </span>
              </div>

              <button className="primary-btn" type="submit" disabled={isLoading || success}>
                {isLoading ? "⏳ Creating Account..." : "Create Account"}
              </button>

              <div className="signin-row">
                Already have an account? <Link to="/login">Sign in</Link>
              </div>
            </form>
          </div>

          <div className="emergency-card">
            <div className="emergency-top">
              <div>
                <div className="emergency-title">⚠ Emergency Situation?</div>
                <div className="emergency-sub">Access emergency features by creating an account.</div>
              </div>
            </div>

            <Link to="/findhelp" className="danger-btn">
              Get Emergency Help Now
            </Link>
          </div>
        </div>

        {/* RIGHT IMAGE */}
        <div className="signup-right" style={{ backgroundImage: "url('/images/Signup.webp')" }}>
          <div className="right-overlay" />
          <div className="right-text">
            <h2>Support when it matters most</h2>
            <p>Designed for doctors and hospitals to respond fast to poisoning cases.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
