import React, { useState } from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import PoisonMap from "../components/PoisonMap";

export default function FindHelp() {
  const [filterType, setFilterType] = useState("all");
  const [viewType, setViewType] = useState("map");

  const hospitals = [
    {
      id: 1,
      name: "Grande Hospital, Thamel",
      category: "Poison Control",
      address: "Thamel, Kathmandu",
      hours: "Open 24/7",
      phone: "+977-1-4123456",
      services: ["Emergency", "ICU", "Poison Clinic"],
      coordinates: [27.716, 85.324],
    },
    {
      id: 2,
      name: "Nepal Police Central Forensic Science Laboratory",
      category: "Urgent Care",
      address: "Kathmandu",
      hours: "9 AM - 5 PM",
      phone: "+977-1-5134934",
      services: ["Forensic Services", "Analysis", "Poison Testing"],
      coordinates: [27.72, 85.32],
    },
  ];

  return (
    <>
      <Navbar />

      {/* PAGE HEADER */}
      <section className="find-help-header">
        <h1>Nearby Emergency Services</h1>
        <p>Find the closest poison control centers and emergency services</p>
      </section>

      {/* LOCATION CARD */}
      <section className="location-services-card">
        <div className="location-card-content">
          <div className="location-icon">📍</div>
          <div className="location-text">
            <h3>Enable Location Services</h3>
            <p>
              Allow us to access your location to find nearby emergency services
            </p>
          </div>
          <button className="btn-get-help-nearby">Get Help Nearby</button>
        </div>
      </section>

      {/* FILTERS AND VIEW OPTIONS */}
      <section className="filters-section">
        <div className="view-options">
          <button
            className={`view-btn ${viewType === "map" ? "active" : ""}`}
            onClick={() => setViewType("map")}
          >
            🗺️ Map View
          </button>
          <button
            className={`view-btn ${viewType === "list" ? "active" : ""}`}
            onClick={() => setViewType("list")}
          >
            📋 List View
          </button>
        </div>

        <div className="filter-buttons">
          <button
            className={`filter-btn ${filterType === "all" ? "active" : ""}`}
            onClick={() => setFilterType("all")}
          >
            All
          </button>
          <button
            className={`filter-btn ${filterType === "poison" ? "active" : ""}`}
            onClick={() => setFilterType("poison")}
          >
            ☠️ Poison Control
          </button>
          <button
            className={`filter-btn ${filterType === "urgent" ? "active" : ""}`}
            onClick={() => setFilterType("urgent")}
          >
            🏥 Urgent Care
          </button>
        </div>
      </section>

      {/* MAP VIEW */}
      {viewType === "map" && (
        <section className="map-view-section">
          <div className="map-wrapper">
            <PoisonMap />
          </div>
        </section>
      )}

      {/* HOSPITALS LIST */}
      <section className="hospitals-section">
        <div className="hospitals-container">
          {hospitals.map((hospital) => (
            <div key={hospital.id} className="hospital-card-page">
              <div className="card-header">
                <div className="category-badge">{hospital.category}</div>
              </div>

              <div className="card-body">
                <h3>{hospital.name}</h3>

                <div className="hospital-info">
                  <div className="info-item">
                    <span className="info-label">📍 Address:</span>
                    <span>{hospital.address}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">🕒 Hours:</span>
                    <span>{hospital.hours}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">📞 Phone:</span>
                    <span>{hospital.phone}</span>
                  </div>
                </div>

                <div className="services-list">
                  {hospital.services.map((service, idx) => (
                    <span key={idx} className="service-tag">
                      {service}
                    </span>
                  ))}
                </div>
              </div>

              <div className="card-actions">
                <button className="btn-call-page">📞 Call Now</button>
                <button className="btn-directions-page">🗺️ Directions</button>
                <button className="btn-details">Details</button>
              </div>
            </div>
          ))}
        </div>
      </section>

      <Footer />
    </>
  );
}
