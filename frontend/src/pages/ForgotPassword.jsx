import React, { useState, useRef, useEffect, useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import authApi from "../api/authApi";
import { getErrorMessage } from "../utils/errorHandler";
import "../styles/Login.css";

/* ── email validation (shared with Login) ── */
const VALID_TLDS = new Set([
  "com","org","net","edu","gov","io","co","in","np","uk",
  "us","ca","au","de","fr","jp","cn","ru","br","mx",
  "info","biz","me","tv","app","dev","tech","online",
  "store","shop","site","xyz","ai",
]);
const COMMON_TYPOS = {
  "gmial.com":"gmail.com","gmal.com":"gmail.com","gamil.com":"gmail.com",
  "gmail.comm":"gmail.com","gmail.con":"gmail.com","gmail.co":"gmail.com",
  "yahooo.com":"yahoo.com","yahoo.comm":"yahoo.com","yahoo.con":"yahoo.com",
  "hotmal.com":"hotmail.com","hotmail.comm":"hotmail.com","hotmail.con":"hotmail.com",
  "outlok.com":"outlook.com","outlook.comm":"outlook.com",
};
const validateEmail = (email) => {
  if (!email || !email.includes("@"))
    return { valid: false, error: "Please enter a valid email address" };
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
    return { valid: false, error: "Please enter a valid email address" };
  const domain = email.split("@")[1].toLowerCase();
  const parts = domain.split(".");
  if (parts.length < 2) return { valid: false, error: "Invalid email domain" };
  if (COMMON_TYPOS[domain])
    return { valid: false, error: `Did you mean ${email.split("@")[0]}@${COMMON_TYPOS[domain]}?` };
  if (!VALID_TLDS.has(parts[parts.length - 1]))
    return { valid: false, error: `Invalid email domain extension ".${parts[parts.length - 1]}"` };
  return { valid: true, error: null };
};

/* ── password strength meter ── */
const getStrength = (p) => {
  let s = 0;
  if (p.length >= 8) s++;
  if (/[A-Z]/.test(p)) s++;
  if (/[a-z]/.test(p)) s++;
  if (/\d/.test(p)) s++;
  if (/[!@#$%^&*(),.?":{}|<>]/.test(p)) s++;
  return s;
};
const strengthLabel = ["", "Very Weak", "Weak", "Fair", "Good", "Strong"];
const strengthColor = ["", "#ef4444", "#f97316", "#eab308", "#22c55e", "#16a34a"];

export default function ForgotPassword() {
  const navigate = useNavigate();

  /* ── state ── */
  const [step, setStep] = useState(1);            // 1 = email, 2 = OTP, 3 = new password
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState(["","","","","",""]);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [devOTP, setDevOTP] = useState(null);
  const [resendCooldown, setResendCooldown] = useState(0);

  const otpRefs = useRef([]);
  const emailValidation = useMemo(() => validateEmail(email), [email]);
  const strength = useMemo(() => getStrength(newPassword), [newPassword]);

  /* cooldown timer */
  useEffect(() => {
    if (resendCooldown <= 0) return;
    const t = setInterval(() => setResendCooldown((p) => (p > 0 ? p - 1 : 0)), 1000);
    return () => clearInterval(t);
  }, [resendCooldown]);

  /* auto-focus first OTP box */
  useEffect(() => {
    if (step === 2 && otpRefs.current[0]) otpRefs.current[0].focus();
  }, [step]);

  /* ── Step 1: request OTP ── */
  const handleRequestOTP = async (e) => {
    e.preventDefault();
    setError(null);
    if (!emailValidation.valid) { setError(emailValidation.error); return; }

    setIsLoading(true);
    try {
      const res = await authApi.forgotPassword(email.toLowerCase());
      // Check dev-mode OTP
      if (res.message?.includes("DEV_MODE")) {
        const m = res.message.match(/DEV_MODE: Your OTP is (\d{6})/);
        if (m) setDevOTP(m[1]);
      }
      setStep(2);
      setResendCooldown(60);
      setSuccess("A 6-digit code has been sent to your email.");
    } catch (err) {
      setError(getErrorMessage(err, "Failed to send reset code. Please try again."));
    } finally {
      setIsLoading(false);
    }
  };

  /* ── Step 2: verify OTP → go to step 3 ── */
  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    setError(null);
    const code = otp.join("");
    if (code.length !== 6) { setError("Please enter the complete 6-digit code."); return; }
    // We don't call backend here — we keep the OTP to send with the password in step 3
    setStep(3);
    setSuccess(null);
  };

  /* ── Step 3: set new password ── */
  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError(null);

    if (newPassword !== confirmPassword) { setError("Passwords do not match."); return; }
    if (strength < 4) { setError("Password is too weak. Use 8+ chars, uppercase, lowercase, number & special character."); return; }

    setIsLoading(true);
    try {
      const code = otp.join("");
      await authApi.resetPassword(email.toLowerCase(), code, newPassword);
      setSuccess("✅ Password reset successfully!");
      setTimeout(() => navigate("/login", { state: { message: "Password reset successfully! Please log in with your new password." } }), 2000);
    } catch (err) {
      const msg = getErrorMessage(err, "Failed to reset password.");
      // If OTP expired / invalid, go back to step 2
      if (msg.toLowerCase().includes("otp") || msg.toLowerCase().includes("expired") || msg.toLowerCase().includes("invalid")) {
        setOtp(["","","","","",""]);
        setStep(2);
      }
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  /* ── resend OTP ── */
  const handleResend = async () => {
    if (resendCooldown > 0) return;
    setError(null);
    setIsLoading(true);
    try {
      const res = await authApi.resendResetOTP(email.toLowerCase());
      if (res.message?.includes("DEV_MODE")) {
        const m = res.message.match(/DEV_MODE: Your OTP is (\d{6})/);
        if (m) setDevOTP(m[1]);
      }
      setOtp(["","","","","",""]);
      setResendCooldown(60);
      setSuccess("✅ New code sent!");
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(getErrorMessage(err, "Failed to resend code."));
    } finally {
      setIsLoading(false);
    }
  };

  /* ── OTP input helpers ── */
  const onOtpChange = (i, v) => {
    if (v && !/^\d$/.test(v)) return;
    const a = [...otp]; a[i] = v; setOtp(a); setError(null);
    if (v && i < 5) otpRefs.current[i + 1].focus();
  };
  const onOtpKey = (i, e) => {
    if (e.key === "Backspace" && !otp[i] && i > 0) otpRefs.current[i - 1].focus();
    if (e.key === "v" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      navigator.clipboard.readText().then((t) => {
        const d = t.replace(/\D/g, "").slice(0, 6);
        if (d.length === 6) { setOtp(d.split("")); otpRefs.current[5].focus(); }
      });
    }
  };
  const onOtpPaste = (e) => {
    e.preventDefault();
    const d = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    if (d.length > 0) {
      const a = [...otp]; d.split("").forEach((c, i) => { if (i < 6) a[i] = c; }); setOtp(a);
      otpRefs.current[Math.min(d.length, 5)].focus();
    }
  };

  /* ── step indicator ── */
  const steps = ["Enter Email", "Verify Code", "New Password"];

  /* ── render ── */
  return (
    <div className="login-split-page">
      <div className="login-split-card">
        {/* LEFT IMAGE PANEL */}
        <div className="login-left">
          <img className="left-bg-img" src="/images/poisonss.jpg" alt="PoisonSense Banner" />
          <div className="left-overlay">
            <div className="left-badge"><span className="dot" />Account Recovery</div>
            <h2 className="left-title">Reset your password</h2>
            <p className="left-desc">
              We'll send a verification code to your registered email address so you can securely set a new password.
            </p>
            <div className="left-points">
              <div className="point">🔒 Secure OTP verification</div>
              <div className="point">📧 Code sent to your email</div>
              <div className="point">✅ Set a strong new password</div>
            </div>
          </div>
        </div>

        {/* RIGHT FORM PANEL */}
        <div className="login-right">
          <button type="button" className="back-home" onClick={() => navigate("/login")}>
            ← Back to Login
          </button>

          <div className="brand-row">
            <img className="brand-logo-img" src="/images/logo.jpg" alt="PoisonSense Logo" />
            <div className="brand-text">
              <div className="brand-title">PoisonSense AI</div>
              <div className="brand-sub">Password Recovery</div>
            </div>
          </div>

          {/* Step indicator */}
          <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
            {steps.map((label, i) => (
              <div key={i} style={{
                flex: 1, textAlign: "center", padding: "8px 0", borderRadius: 8,
                fontSize: 12, fontWeight: 800,
                background: step === i + 1 ? "linear-gradient(135deg,#2563eb,#0ea5e9)" : step > i + 1 ? "#22c55e" : "#e2e8f0",
                color: step >= i + 1 ? "#fff" : "#64748b",
                transition: "all .3s",
              }}>
                {step > i + 1 ? "✓ " : ""}{label}
              </div>
            ))}
          </div>

          {error && <div className="alert error">⚠️ {error}</div>}
          {success && <div className="alert info" style={{ backgroundColor: "#e8f5e9", color: "#2e7d32", border: "1px solid #4caf50", padding: "10px 12px", borderRadius: 12, marginBottom: 10, fontWeight: 900, fontSize: 13 }}>✅ {success}</div>}

          {/* ── STEP 1 — Email ── */}
          {step === 1 && (
            <form onSubmit={handleRequestOTP} className="login-form">
              <label className="label">Email Address</label>
              <div className={`input-wrap ${email && !emailValidation.valid ? "error-border" : email && emailValidation.valid ? "success-border" : ""}`}>
                <input type="email" placeholder="you@example.com" required value={email}
                  onChange={(e) => setEmail(e.target.value)} />
              </div>
              {email && !emailValidation.valid && <p className="mini-error">⚠️ {emailValidation.error}</p>}

              <button type="submit" className="btn-main" disabled={isLoading} style={{ marginTop: 22 }}>
                {isLoading ? "⏳ Sending Code..." : "Send Reset Code"}
              </button>

              <div className="signup-text" style={{ marginTop: 16 }}>
                Remember your password? <Link to="/login">Sign in</Link>
              </div>
            </form>
          )}

          {/* ── STEP 2 — OTP ── */}
          {step === 2 && (
            <form onSubmit={handleVerifyOTP} className="login-form">
              <div style={{ textAlign: "center", marginBottom: 12 }}>
                <div style={{ fontSize: 36, marginBottom: 4 }}>📧</div>
                <p style={{ fontWeight: 800, color: "#334155", margin: 0 }}>Enter the 6-digit code sent to</p>
                <p style={{ fontWeight: 900, color: "#2563eb", margin: "4px 0 0" }}>{email}</p>
              </div>

              {/* Dev-mode OTP banner */}
              {devOTP && (
                <div style={{
                  backgroundColor: "#fff3cd", border: "2px dashed #ffc107", borderRadius: 12,
                  padding: "12px 16px", marginBottom: 16, textAlign: "center",
                }}>
                  <div style={{ fontSize: 11, color: "#856404", fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>
                    🛠️ Dev Mode — Email not configured
                  </div>
                  <div style={{ fontSize: 28, fontWeight: "bold", letterSpacing: 8, color: "#d63384", fontFamily: "monospace" }}>
                    {devOTP}
                  </div>
                </div>
              )}

              {/* OTP boxes */}
              <div style={{ display: "flex", gap: 10, justifyContent: "center", margin: "16px 0" }}>
                {otp.map((d, i) => (
                  <input key={i} ref={(el) => (otpRefs.current[i] = el)}
                    type="text" inputMode="numeric" maxLength={1}
                    value={d} onChange={(e) => onOtpChange(i, e.target.value)}
                    onKeyDown={(e) => onOtpKey(i, e)} onPaste={onOtpPaste}
                    style={{
                      width: 48, height: 56, textAlign: "center", fontSize: 24, fontWeight: 800,
                      border: d ? "2px solid #2563eb" : "2px solid #dbe3ee", borderRadius: 12,
                      outline: "none", transition: "all .2s",
                    }}
                    onFocus={(e) => (e.target.style.boxShadow = "0 0 0 4px rgba(37,99,235,.15)")}
                    onBlur={(e) => (e.target.style.boxShadow = "none")}
                  />
                ))}
              </div>

              <button type="submit" className="btn-main" disabled={isLoading || otp.join("").length !== 6}>
                Verify Code
              </button>

              <div style={{ textAlign: "center", marginTop: 14 }}>
                <button type="button" disabled={resendCooldown > 0 || isLoading}
                  onClick={handleResend}
                  style={{
                    background: "none", border: "none", cursor: resendCooldown > 0 ? "not-allowed" : "pointer",
                    fontWeight: 800, fontSize: 13,
                    color: resendCooldown > 0 ? "#94a3b8" : "#2563eb",
                  }}>
                  {resendCooldown > 0 ? `Resend code in ${resendCooldown}s` : "Resend Code"}
                </button>
              </div>

              <div className="signup-text" style={{ marginTop: 10 }}>
                <button type="button" onClick={() => { setStep(1); setError(null); setSuccess(null); setDevOTP(null); }}
                  style={{ background: "none", border: "none", color: "#2563eb", fontWeight: 900, cursor: "pointer", fontSize: 14 }}>
                  ← Change email
                </button>
              </div>
            </form>
          )}

          {/* ── STEP 3 — New Password ── */}
          {step === 3 && (
            <form onSubmit={handleResetPassword} className="login-form">
              <div style={{ textAlign: "center", marginBottom: 12 }}>
                <div style={{ fontSize: 36, marginBottom: 4 }}>🔐</div>
                <p style={{ fontWeight: 800, color: "#334155", margin: 0 }}>Create a new password</p>
              </div>

              <label className="label">New Password</label>
              <div className="input-wrap">
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Min. 8 characters"
                  required value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                />
              </div>

              {/* Strength bar */}
              {newPassword && (
                <div style={{ marginTop: 8 }}>
                  <div style={{ display: "flex", gap: 4 }}>
                    {[1,2,3,4,5].map((n) => (
                      <div key={n} style={{
                        flex: 1, height: 4, borderRadius: 2,
                        background: strength >= n ? strengthColor[strength] : "#e2e8f0",
                        transition: ".3s",
                      }} />
                    ))}
                  </div>
                  <p style={{ fontSize: 12, fontWeight: 700, color: strengthColor[strength], margin: "4px 0 0" }}>
                    {strengthLabel[strength]}
                  </p>
                </div>
              )}

              <label className="label">Confirm Password</label>
              <div className={`input-wrap ${confirmPassword && confirmPassword !== newPassword ? "error-border" : confirmPassword && confirmPassword === newPassword ? "success-border" : ""}`}>
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Re-enter password"
                  required value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </div>
              {confirmPassword && confirmPassword !== newPassword && (
                <p className="mini-error">⚠️ Passwords do not match</p>
              )}

              <label style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 10, fontWeight: 800, fontSize: 13, cursor: "pointer" }}>
                <input type="checkbox" checked={showPassword} onChange={(e) => setShowPassword(e.target.checked)} />
                Show passwords
              </label>

              <button type="submit" className="btn-main" disabled={isLoading || !newPassword || newPassword !== confirmPassword || strength < 4}
                style={{ marginTop: 18 }}>
                {isLoading ? "⏳ Resetting..." : "Reset Password"}
              </button>
            </form>
          )}

        </div>
      </div>
    </div>
  );
}
