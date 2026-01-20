import React, { useState } from "react";
import { Link } from "react-router-dom";

export default function Login() {
  const [remember, setRemember] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();

    // ✅ Collect form values
    const formData = new FormData(e.currentTarget);
    const email = formData.get("email");
    const password = formData.get("password");
    const rememberMe = formData.get("remember") === "on";

    console.log({ email, password, rememberMe });

    // ✅ Connect your backend API here
    alert("Login form submitted ✅ (connect backend API)");
  };

  return (
    <div className="auth-body">
      <div className="auth-container">
        {/* Logo / Header */}
        <div className="auth-header">
          {/* ✅ Logo should be in: frontend/public/images/logo.jpg */}
          <img src="/images/logo.jpg" alt="PoisonSense AI" />
          <h2>PoisonSense AI</h2>
          <h3>Welcome Back</h3>
          <p>Sign in to access emergency support</p>
        </div>

        {/* Login Form */}
        <form className="auth-form" onSubmit={handleSubmit}>
          <label>Email Address</label>
          <div className="input-box">
            <input
              type="email"
              name="email"
              placeholder="your.email@example.com"
              required
            />
          </div>

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

          <button type="submit" className="btn-primary">
            ➡️ Sign In
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
