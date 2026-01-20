import React, { useState } from "react";
import { Link } from "react-router-dom";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <img
            src="/images/logo.jpg"
            alt="PoisonSense AI Logo"
            className="logo-image"
          />
          PoisonSense AI
        </Link>
        <div className="menu-icon" onClick={() => setIsOpen(!isOpen)}>
          <i className={isOpen ? "fas fa-times" : "fas fa-bars"}></i>
        </div>
        <ul className={isOpen ? "nav-menu active" : "nav-menu"}>
          <li className="nav-item">
            <Link to="/" className="nav-link" onClick={() => setIsOpen(false)}>
              Home
            </Link>
          </li>
          <li className="nav-item">
            <Link
              to="/ai-assistant"
              className="nav-link"
              onClick={() => setIsOpen(false)}
            >
              AI Assistant
            </Link>
          </li>
          <li className="nav-item">
            <Link
              to="/find-help"
              className="nav-link"
              onClick={() => setIsOpen(false)}
            >
              Find Help
            </Link>
          </li>
          <li className="nav-item">
            <Link
              to="#profile"
              className="nav-link"
              onClick={() => setIsOpen(false)}
            >
              Profile
            </Link>
          </li>
          <li className="nav-item">
            <Link
              to="/login"
              className="nav-link"
              onClick={() => setIsOpen(false)}
            >
              Login
            </Link>
          </li>
          <li className="nav-item">
            <Link
              to="/signup"
              className="nav-link"
              onClick={() => setIsOpen(false)}
            >
              Sign Up
            </Link>
          </li>
          <li className="nav-item">
            <a
              href="tel:102"
              className="nav-link emergency-btn"
              onClick={() => setIsOpen(false)}
            >
              📞 Call 102
            </a>
          </li>
        </ul>
      </div>
    </nav>
  );
}
