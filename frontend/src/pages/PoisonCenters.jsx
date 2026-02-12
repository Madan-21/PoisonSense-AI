import React, { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { centerApi } from "../api/centerApi";
import { getErrorMessage } from "../utils/errorHandler";

export default function PoisonCenters() {
  const [centers, setCenters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("all"); // all, 24hours, govt

  useEffect(() => {
    fetchPoisonCenters();
  }, []);

  const fetchPoisonCenters = async () => {
    try {
      setLoading(true);
      const data = await centerApi.getAllPoisonCenters();
      setCenters(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error fetching poison centers:", err);
      setError(getErrorMessage(err, "Failed to load poison centers. Please check if backend is running."));
    } finally {
      setLoading(false);
    }
  };

  const getFilteredCenters = () => {
    if (filter === "24hours") {
      return centers.filter(c => c.is_24_hours);
    }
    if (filter === "govt") {
      return centers.filter(c => c.government_affiliated);
    }
    return centers;
  };

  const filteredCenters = getFilteredCenters();

  return (
    <>
      <Navbar />
      
      <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "20px" }}>
        {/* Header */}
        <section style={{ textAlign: "center", padding: "40px 20px", background: "linear-gradient(135deg, #dc3545 0%, #b02a37 100%)", color: "white", borderRadius: "16px", marginBottom: "30px" }}>
          <h1 style={{ fontSize: "2.5rem", marginBottom: "10px" }}>☠️ Poison Control Centers</h1>
          <p style={{ fontSize: "1.2rem", opacity: 0.9 }}>24/7 Emergency Toxicology Support Across India</p>
          <div style={{ marginTop: "20px", padding: "15px", background: "rgba(255,255,255,0.2)", borderRadius: "8px", display: "inline-block" }}>
            <span style={{ fontSize: "1.5rem", fontWeight: "bold" }}>📞 National Poison Helpline: 1800-116-117</span>
          </div>
        </section>

        {/* Filter Buttons */}
        <div style={{ display: "flex", gap: "10px", marginBottom: "20px", flexWrap: "wrap" }}>
          <button
            onClick={() => setFilter("all")}
            style={{
              padding: "10px 20px",
              border: "none",
              borderRadius: "8px",
              cursor: "pointer",
              background: filter === "all" ? "#dc3545" : "#e9ecef",
              color: filter === "all" ? "white" : "#333",
              fontWeight: filter === "all" ? "bold" : "normal"
            }}
          >
            All Centers ({centers.length})
          </button>
          <button
            onClick={() => setFilter("24hours")}
            style={{
              padding: "10px 20px",
              border: "none",
              borderRadius: "8px",
              cursor: "pointer",
              background: filter === "24hours" ? "#dc3545" : "#e9ecef",
              color: filter === "24hours" ? "white" : "#333",
              fontWeight: filter === "24hours" ? "bold" : "normal"
            }}
          >
            🕐 24/7 Centers
          </button>
          <button
            onClick={() => setFilter("govt")}
            style={{
              padding: "10px 20px",
              border: "none",
              borderRadius: "8px",
              cursor: "pointer",
              background: filter === "govt" ? "#dc3545" : "#e9ecef",
              color: filter === "govt" ? "white" : "#333",
              fontWeight: filter === "govt" ? "bold" : "normal"
            }}
          >
            🏛️ Government Centers
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div style={{ textAlign: "center", padding: "60px" }}>
            <div style={{ fontSize: "48px", marginBottom: "20px" }}>⏳</div>
            <p>Loading poison control centers...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div style={{ 
            background: "#f8d7da", 
            color: "#721c24", 
            padding: "20px", 
            borderRadius: "8px", 
            marginBottom: "20px",
            textAlign: "center"
          }}>
            ⚠️ {error}
            <br />
            <button onClick={fetchPoisonCenters} style={{ marginTop: "10px", padding: "8px 16px", cursor: "pointer" }}>
              Retry
            </button>
          </div>
        )}

        {/* Centers List */}
        {!loading && !error && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(350px, 1fr))", gap: "20px" }}>
            {filteredCenters.length === 0 ? (
              <div style={{ gridColumn: "1/-1", textAlign: "center", padding: "40px" }}>
                <div style={{ fontSize: "48px", marginBottom: "20px" }}>🔍</div>
                <p>No poison centers found matching your filter.</p>
              </div>
            ) : (
              filteredCenters.map((center) => (
                <div key={center.id} style={{
                  background: "white",
                  borderRadius: "12px",
                  boxShadow: "0 2px 12px rgba(0,0,0,0.1)",
                  overflow: "hidden",
                  border: "1px solid #e9ecef"
                }}>
                  {/* Card Header */}
                  <div style={{ 
                    background: "linear-gradient(135deg, #dc3545, #b02a37)",
                    color: "white",
                    padding: "15px"
                  }}>
                    <h3 style={{ margin: "0 0 5px 0", fontSize: "1.1rem" }}>{center.name}</h3>
                    <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                      {center.is_24_hours && (
                        <span style={{ background: "rgba(255,255,255,0.2)", padding: "3px 8px", borderRadius: "4px", fontSize: "12px" }}>
                          🕐 24/7
                        </span>
                      )}
                      {center.is_verified && (
                        <span style={{ background: "rgba(255,255,255,0.2)", padding: "3px 8px", borderRadius: "4px", fontSize: "12px" }}>
                          ✅ Verified
                        </span>
                      )}
                      {center.government_affiliated && (
                        <span style={{ background: "rgba(255,255,255,0.2)", padding: "3px 8px", borderRadius: "4px", fontSize: "12px" }}>
                          🏛️ Govt
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Card Body */}
                  <div style={{ padding: "15px" }}>
                    <div style={{ marginBottom: "12px" }}>
                      <div style={{ color: "#666", fontSize: "14px", marginBottom: "4px" }}>📍 Location</div>
                      <div>{center.address}, {center.city}</div>
                    </div>

                    <div style={{ marginBottom: "12px" }}>
                      <div style={{ color: "#666", fontSize: "14px", marginBottom: "4px" }}>📞 Phone</div>
                      <div style={{ fontWeight: "bold", color: "#dc3545" }}>{center.phone_primary}</div>
                      {center.phone_secondary && (
                        <div style={{ color: "#666" }}>{center.phone_secondary}</div>
                      )}
                    </div>

                    {center.toll_free_number && (
                      <div style={{ marginBottom: "12px" }}>
                        <div style={{ color: "#666", fontSize: "14px", marginBottom: "4px" }}>📞 Toll-Free</div>
                        <div style={{ fontWeight: "bold", color: "#28a745", fontSize: "1.1rem" }}>
                          {center.toll_free_number}
                        </div>
                      </div>
                    )}

                    {center.services && center.services.length > 0 && (
                      <div style={{ marginBottom: "12px" }}>
                        <div style={{ color: "#666", fontSize: "14px", marginBottom: "4px" }}>🛠️ Services</div>
                        <div style={{ display: "flex", gap: "5px", flexWrap: "wrap" }}>
                          {center.services.slice(0, 3).map((service, idx) => (
                            <span key={idx} style={{
                              background: "#e9ecef",
                              padding: "3px 8px",
                              borderRadius: "4px",
                              fontSize: "12px"
                            }}>
                              {service}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Card Actions */}
                  <div style={{ 
                    padding: "15px", 
                    borderTop: "1px solid #e9ecef",
                    display: "flex",
                    gap: "10px"
                  }}>
                    <a
                      href={`tel:${center.phone_primary}`}
                      style={{
                        flex: 1,
                        padding: "10px",
                        background: "#dc3545",
                        color: "white",
                        textAlign: "center",
                        borderRadius: "8px",
                        textDecoration: "none",
                        fontWeight: "bold"
                      }}
                    >
                      📞 Call Now
                    </a>
                    {center.latitude && center.longitude && (
                      <a
                        href={`https://www.google.com/maps/dir/?api=1&destination=${center.latitude},${center.longitude}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          flex: 1,
                          padding: "10px",
                          background: "#28a745",
                          color: "white",
                          textAlign: "center",
                          borderRadius: "8px",
                          textDecoration: "none",
                          fontWeight: "bold"
                        }}
                      >
                        🗺️ Directions
                      </a>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Emergency Info */}
        <section style={{
          marginTop: "40px",
          padding: "30px",
          background: "#fff3cd",
          borderRadius: "12px",
          border: "2px solid #ffc107"
        }}>
          <h3 style={{ textAlign: "center", marginBottom: "20px" }}>🚨 In Case of Emergency</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "20px", textAlign: "center" }}>
            <div>
              <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#dc3545" }}>102</div>
              <div>Ambulance</div>
            </div>
            <div>
              <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#dc3545" }}>1800-116-117</div>
              <div>National Poison Centre</div>
            </div>
            <div>
              <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#dc3545" }}>112</div>
              <div>Emergency Services</div>
            </div>
            <div>
              <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#dc3545" }}>100</div>
              <div>Police</div>
            </div>
          </div>
        </section>
      </div>

      <Footer />
    </>
  );
}
