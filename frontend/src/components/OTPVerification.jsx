import React, { useState, useRef, useEffect } from "react";
import { useAuth } from "../context/AuthContext";

export default function OTPVerification({ email, onVerified, onBack, devModeOTP }) {
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [devOTP, setDevOTP] = useState(devModeOTP || null);
  const inputRefs = useRef([]);
  
  const { verifyOTP, resendOTP } = useAuth();

  // Start cooldown timer on mount
  useEffect(() => {
    setResendCooldown(60); // 60 second cooldown initially
    const timer = setInterval(() => {
      setResendCooldown((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Focus first input on mount
  useEffect(() => {
    if (inputRefs.current[0]) {
      inputRefs.current[0].focus();
    }
  }, []);

  const handleChange = (index, value) => {
    // Only allow digits
    if (value && !/^\d$/.test(value)) return;

    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);
    setError(null);

    // Auto-focus next input
    if (value && index < 5) {
      inputRefs.current[index + 1].focus();
    }
  };

  const handleKeyDown = (index, e) => {
    // Handle backspace - move to previous input
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      inputRefs.current[index - 1].focus();
    }
    
    // Handle paste
    if (e.key === "v" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      navigator.clipboard.readText().then((text) => {
        const digits = text.replace(/\D/g, "").slice(0, 6);
        if (digits.length === 6) {
          setOtp(digits.split(""));
          inputRefs.current[5].focus();
        }
      });
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData("text");
    const digits = pastedData.replace(/\D/g, "").slice(0, 6);
    if (digits.length > 0) {
      const newOtp = [...otp];
      digits.split("").forEach((digit, i) => {
        if (i < 6) newOtp[i] = digit;
      });
      setOtp(newOtp);
      const focusIndex = Math.min(digits.length, 5);
      inputRefs.current[focusIndex].focus();
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    const otpString = otp.join("");
    if (otpString.length !== 6) {
      setError("Please enter the complete 6-digit code");
      return;
    }

    setIsLoading(true);
    try {
      const response = await verifyOTP(email, otpString);
      setSuccess("✅ Email verified successfully!");
      
      // Call onVerified callback after a short delay
      setTimeout(() => {
        onVerified(response);
      }, 1500);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || "Verification failed";
      setError(errorMsg);
      // Clear OTP on error
      setOtp(["", "", "", "", "", ""]);
      inputRefs.current[0].focus();
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    if (resendCooldown > 0) return;
    
    setError(null);
    setIsLoading(true);
    try {
      const response = await resendOTP(email);
      
      // Check if DEV_MODE OTP is returned
      if (response.message && response.message.includes("DEV_MODE")) {
        const otpMatch = response.message.match(/DEV_MODE: Your OTP is (\d{6})/);
        if (otpMatch) {
          setDevOTP(otpMatch[1]);
        }
      }
      
      setSuccess("✅ New verification code sent!");
      setResendCooldown(60); // Reset cooldown
      setOtp(["", "", "", "", "", ""]);
      inputRefs.current[0].focus();
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to resend code");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="otp-verification">
      <div className="otp-header">
        <div className="otp-icon">📧</div>
        <h2>Verify Your Email</h2>
        <p>We've sent a 6-digit verification code to:</p>
        <p className="otp-email">{email}</p>
      </div>

      {/* Development Mode OTP Display */}
      {devOTP && (
        <div className="dev-mode-otp" style={{
          backgroundColor: '#fff3cd',
          border: '2px dashed #ffc107',
          borderRadius: '12px',
          padding: '15px 20px',
          marginBottom: '20px',
          textAlign: 'center'
        }}>
          <div style={{ 
            fontSize: '12px', 
            color: '#856404', 
            marginBottom: '8px',
            fontWeight: '600',
            textTransform: 'uppercase',
            letterSpacing: '1px'
          }}>
            🛠️ Development Mode
          </div>
          <div style={{ 
            fontSize: '14px', 
            color: '#856404', 
            marginBottom: '10px' 
          }}>
            Email service not configured. Your OTP is:
          </div>
          <div style={{
            fontSize: '32px',
            fontWeight: 'bold',
            letterSpacing: '8px',
            color: '#d63384',
            backgroundColor: '#fff',
            padding: '10px 20px',
            borderRadius: '8px',
            display: 'inline-block',
            fontFamily: 'monospace'
          }}>
            {devOTP}
          </div>
        </div>
      )}

      <form onSubmit={handleVerify}>
        {error && (
          <div className="error-message" style={{
            color: '#dc3545',
            backgroundColor: '#f8d7da',
            padding: '10px',
            borderRadius: '8px',
            marginBottom: '15px',
            fontSize: '14px',
            textAlign: 'center'
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
            fontSize: '14px',
            textAlign: 'center'
          }}>
            {success}
          </div>
        )}

        <div className="otp-inputs" style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '10px',
          marginBottom: '20px'
        }}>
          {otp.map((digit, index) => (
            <input
              key={index}
              ref={(el) => (inputRefs.current[index] = el)}
              type="text"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onChange={(e) => handleChange(index, e.target.value)}
              onKeyDown={(e) => handleKeyDown(index, e)}
              onPaste={handlePaste}
              disabled={isLoading || success}
              style={{
                width: '50px',
                height: '60px',
                fontSize: '24px',
                textAlign: 'center',
                border: '2px solid #ddd',
                borderRadius: '10px',
                outline: 'none',
                transition: 'all 0.2s',
                backgroundColor: digit ? '#f0f9ff' : '#fff',
                borderColor: digit ? '#0ea5e9' : '#ddd'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#0ea5e9';
                e.target.style.boxShadow = '0 0 0 3px rgba(14, 165, 233, 0.2)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = digit ? '#0ea5e9' : '#ddd';
                e.target.style.boxShadow = 'none';
              }}
            />
          ))}
        </div>

        <button
          type="submit"
          className="btn-primary"
          disabled={isLoading || otp.join("").length !== 6 || success}
          style={{
            width: '100%',
            padding: '14px',
            fontSize: '16px',
            cursor: isLoading || otp.join("").length !== 6 ? 'not-allowed' : 'pointer',
            opacity: isLoading || otp.join("").length !== 6 ? 0.7 : 1
          }}
        >
          {isLoading ? "⏳ Verifying..." : success ? "✅ Verified!" : "🔐 Verify Email"}
        </button>
      </form>

      <div className="otp-footer" style={{ marginTop: '20px', textAlign: 'center' }}>
        <p style={{ color: '#666', marginBottom: '10px' }}>
          Didn't receive the code?
        </p>
        <button
          onClick={handleResend}
          disabled={resendCooldown > 0 || isLoading}
          style={{
            background: 'none',
            border: 'none',
            color: resendCooldown > 0 ? '#999' : '#0ea5e9',
            cursor: resendCooldown > 0 ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            textDecoration: 'underline'
          }}
        >
          {resendCooldown > 0 ? `Resend in ${resendCooldown}s` : "Resend Code"}
        </button>

        <div style={{ marginTop: '20px' }}>
          <button
            onClick={onBack}
            style={{
              background: 'none',
              border: '1px solid #ddd',
              padding: '10px 20px',
              borderRadius: '8px',
              cursor: 'pointer',
              color: '#666'
            }}
          >
            ← Back to Signup
          </button>
        </div>
      </div>

      <div style={{
        marginTop: '20px',
        padding: '15px',
        backgroundColor: '#fff3cd',
        borderRadius: '8px',
        fontSize: '13px',
        color: '#856404'
      }}>
        <strong>💡 Tip:</strong> Check your spam/junk folder if you don't see the email.
        The code expires in 10 minutes.
      </div>
    </div>
  );
}
