import React, { useMemo, useState } from "react";

export default function Signup() {
  const [role, setRole] = useState("");
  const [pass, setPass] = useState("");
  const [confirmPass, setConfirmPass] = useState("");

  const passwordsMatch = useMemo(() => pass === confirmPass, [pass, confirmPass]);
  const showPassError = useMemo(
    () => (pass.length > 0 || confirmPass.length > 0) && !passwordsMatch,
    [pass, confirmPass, passwordsMatch]
  );

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

    if (!role) {
      alert("Please select an account type.");
      return;
    }
    if (!passwordsMatch) {
      alert("Passwords do not match.");
      return;
    }

    const form = e.currentTarget;
    const formData = new FormData(form);

    console.log("FormData ready to submit:");
    alert("Signup form valid ✅ (connect backend API to submit)");
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
            />
          </div>

          <div className="input-row">
            <div>
              <label>Email Address *</label>
              <div className="input-box">
                <input
                  type="email"
                  name="email"
                  placeholder="your.email@example.com"
                  required
                />
              </div>
            </div>

            <div>
              <label>Phone Number *</label>
              <div className="input-box">
                <input type="tel" name="phone" placeholder="98XXXXXXXX" required />
              </div>
            </div>
          </div>

          <div className="input-row">
            <div>
              <label>Password *</label>
              <div className="input-box">
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
            </div>

            <div>
              <label>Confirm Password *</label>
              <div className="input-box">
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

          <button type="submit" className="btn-primary">
            👤 Create Account
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
