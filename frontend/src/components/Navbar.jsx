import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";

// SVG Icons matching Figma design
const HomeIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
    <polyline points="9 22 9 12 15 12 15 22"></polyline>
  </svg>
);

const ChatIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="18" height="14" rx="2" ry="2"></rect>
    <line x1="7" y1="8" x2="17" y2="8"></line>
    <line x1="7" y1="12" x2="13" y2="12"></line>
  </svg>
);

const ActivityIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
  </svg>
);

const MapPinIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
    <circle cx="12" cy="10" r="3"></circle>
  </svg>
);

const UserIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
    <circle cx="12" cy="7" r="4"></circle>
  </svg>
);

const PhoneIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
  </svg>
);

const PillIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10.5 20.5L3.5 13.5C2.1 12.1 2.1 9.9 3.5 8.5L8.5 3.5C9.9 2.1 12.1 2.1 13.5 3.5L20.5 10.5C21.9 11.9 21.9 14.1 20.5 15.5L15.5 20.5C14.1 21.9 11.9 21.9 10.5 20.5Z"></path>
    <path d="M8.5 8.5L15.5 15.5"></path>
  </svg>
);

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar-new">
      <div className="navbar-container-new">
        <Link to="/" className="navbar-logo-new">
          <img
            src="/images/logo.jpg"
            alt="PoisonSense AI Logo"
            className="logo-image-new"
          />
          <span>PoisonSense AI</span>
        </Link>
        
        <div className="menu-icon-new" onClick={() => setIsOpen(!isOpen)}>
          {isOpen ? "✕" : "☰"}
        </div>
        
        <ul className={isOpen ? "nav-menu-new active" : "nav-menu-new"}>
          <li className="nav-item-new">
            <Link to="/" className={`nav-link-new ${isActive('/') ? 'active' : ''}`} onClick={() => setIsOpen(false)}>
              <HomeIcon />
              Home
            </Link>
          </li>
          <li className="nav-item-new">
            <Link
              to="/ai-assistant"
              className={`nav-link-new ${isActive('/ai-assistant') ? 'active' : ''}`}
              onClick={() => setIsOpen(false)}
            >
              <ChatIcon />
              AI Assistant
            </Link>
          </li>
          <li className="nav-item-new">
            <Link
              to="/risk-assessment"
              className={`nav-link-new ${isActive('/risk-assessment') ? 'active' : ''}`}
              onClick={() => setIsOpen(false)}
            >
              <ActivityIcon />
              Risk Assessment
            </Link>
          </li>
          <li className="nav-item-new">
            <Link
              to="/find-help"
              className={`nav-link-new ${isActive('/find-help') ? 'active' : ''}`}
              onClick={() => setIsOpen(false)}
            >
              <MapPinIcon />
              Find Help
            </Link>
          </li>
          <li className="nav-item-new">
            <Link
              to="/poison-management"
              className={`nav-link-new ${isActive('/poison-management') || isActive('/antidotes') ? 'active' : ''}`}
              onClick={() => setIsOpen(false)}
            >
              <PillIcon />
              Antidotes
            </Link>
          </li>
          <li className="nav-item-new">
            <Link
              to="/profile"
              className={`nav-link-new ${isActive('/profile') ? 'active' : ''}`}
              onClick={() => setIsOpen(false)}
            >
              <UserIcon />
              Profile
            </Link>
          </li>
          <li className="nav-item-new">
            <Link
              to="/login"
              className={`nav-link-new ${isActive('/login') ? 'active' : ''}`}
              onClick={() => setIsOpen(false)}
            >
              <UserIcon />
              Login
            </Link>
          </li>
          <li className="nav-item-new">
            <a
              href="tel:102"
              className="nav-link-new emergency-btn-new"
              onClick={() => setIsOpen(false)}
            >
              <PhoneIcon />
              Call 102
            </a>
          </li>
        </ul>
      </div>
    </nav>
  );
}
