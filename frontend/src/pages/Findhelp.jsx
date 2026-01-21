import React, { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import PoisonMap from "../components/PoisonMap";
import { centerApi } from "../api/centerApi";

export default function FindHelp() {
  const [filterType, setFilterType] = useState("all");
  const [viewType, setViewType] = useState("map");
  const [userLocation, setUserLocation] = useState(null);
  const [hospitals, setHospitals] = useState([]);
  const [poisonCenters, setPoisonCenters] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [locationStatus, setLocationStatus] = useState("idle"); // idle, loading, granted, denied

  // Get user location and fetch nearby resources
  const getLocationAndFetchData = async () => {
    setLocationStatus("loading");
    setError(null);
    
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by your browser");
      setLocationStatus("denied");
      // Fetch all data without location
      fetchAllData();
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        setUserLocation({ latitude, longitude });
        setLocationStatus("granted");
        await fetchNearbyData(latitude, longitude);
      },
      (error) => {
        console.error("Location error:", error);
        setLocationStatus("denied");
        setError("Location access denied. Showing all centers.");
        // Fetch all data without location
        fetchAllData();
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  // Fetch nearby hospitals and poison centers
  const fetchNearbyData = async (latitude, longitude) => {
    setLoading(true);
    try {
      const [hospitalsRes, centersRes] = await Promise.all([
        centerApi.getNearbyHospitals(latitude, longitude, { radiusKm: 500, limit: 20 }),
        centerApi.getNearbyPoisonCenters(latitude, longitude, { radiusKm: 1000, limit: 20 })
      ]);
      
      const hospitalsData = hospitalsRes.hospitals || hospitalsRes || [];
      const centersData = centersRes.centers || centersRes || [];
      
      setHospitals(hospitalsData);
      setPoisonCenters(centersData);
      
      // If no nearby results, fetch all
      if (hospitalsData.length === 0 && centersData.length === 0) {
        console.log("No nearby resources, fetching all...");
        await fetchAllData();
      }
    } catch (err) {
      console.error("Error fetching nearby data:", err);
      setError("Failed to fetch nearby resources. Loading all centers...");
      await fetchAllData();
    } finally {
      setLoading(false);
    }
  };

  // Fetch all data without location filter
  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [hospitalsRes, centersRes] = await Promise.all([
        centerApi.getAllHospitals(),
        centerApi.getAllPoisonCenters()
      ]);
      
      setHospitals(Array.isArray(hospitalsRes) ? hospitalsRes : []);
      setPoisonCenters(Array.isArray(centersRes) ? centersRes : []);
    } catch (err) {
      console.error("Error fetching all data:", err);
      setError("Failed to load emergency services. Please check if the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  // Auto-load on mount
  useEffect(() => {
    getLocationAndFetchData();
  }, []);

  // Filter displayed items
  const getFilteredItems = () => {
    let items = [];
    
    if (filterType === "all" || filterType === "poison") {
      items = [...items, ...poisonCenters.map(c => ({ ...c, type: "poison" }))];
    }
    
    if (filterType === "all" || filterType === "urgent") {
      items = [...items, ...hospitals.map(h => ({ ...h, type: "hospital" }))];
    }
    
    return items;
  };

  const filteredItems = getFilteredItems();

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
          <div className="location-icon">
            {locationStatus === "loading" ? "⏳" : 
             locationStatus === "granted" ? "✅" : "📍"}
          </div>
          <div className="location-text">
            <h3>
              {locationStatus === "granted" 
                ? "Location Enabled" 
                : locationStatus === "loading" 
                ? "Getting Location..." 
                : "Enable Location Services"}
            </h3>
            <p>
              {locationStatus === "granted" 
                ? `Showing resources near you (${userLocation?.latitude.toFixed(4)}, ${userLocation?.longitude.toFixed(4)})` 
                : "Allow us to access your location to find nearby emergency services"}
            </p>
          </div>
          <button 
            className="btn-get-help-nearby" 
            onClick={getLocationAndFetchData}
            disabled={loading}
          >
            {loading ? "Loading..." : locationStatus === "granted" ? "Refresh" : "Get Help Nearby"}
          </button>
        </div>
        
        {error && (
          <div style={{ color: '#dc3545', padding: '10px', textAlign: 'center' }}>
            ⚠️ {error}
          </div>
        )}
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
            All ({poisonCenters.length + hospitals.length})
          </button>
          <button
            className={`filter-btn ${filterType === "poison" ? "active" : ""}`}
            onClick={() => setFilterType("poison")}
          >
            ☠️ Poison Control ({poisonCenters.length})
          </button>
          <button
            className={`filter-btn ${filterType === "urgent" ? "active" : ""}`}
            onClick={() => setFilterType("urgent")}
          >
            🏥 Hospitals ({hospitals.length})
          </button>
        </div>
      </section>

      {/* MAP VIEW - WITH LOCATION PERMISSION REQUEST */}
      {viewType === "map" && (
        <section className="map-view-section">
          {locationStatus === "idle" || locationStatus === "denied" ? (
            // Location Permission Request Modal
            <div style={{
              background: "linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
              borderRadius: "16px",
              padding: "40px",
              textAlign: "center",
              maxWidth: "500px",
              margin: "20px auto",
              boxShadow: "0 4px 20px rgba(0,0,0,0.1)"
            }}>
              <div style={{ fontSize: "64px", marginBottom: "20px" }}>📍</div>
              <h2 style={{ marginBottom: "15px", color: "#333" }}>Enable Location Services</h2>
              <p style={{ color: "#666", marginBottom: "25px", lineHeight: "1.6" }}>
                To show emergency services near you on the map, we need access to your location.
                This helps us find the closest hospitals and poison control centers.
              </p>
              
              <div style={{
                background: "#fff3cd",
                padding: "15px",
                borderRadius: "8px",
                marginBottom: "25px",
                fontSize: "14px",
                color: "#856404"
              }}>
                <strong>🔒 Privacy Note:</strong> Your location is only used to find nearby services
                and is not stored or shared with third parties.
              </div>

              <button
                onClick={getLocationAndFetchData}
                disabled={loading}
                style={{
                  background: "linear-gradient(135deg, #28a745 0%, #1a5f2a 100%)",
                  color: "white",
                  border: "none",
                  padding: "15px 40px",
                  borderRadius: "30px",
                  fontSize: "18px",
                  fontWeight: "bold",
                  cursor: loading ? "not-allowed" : "pointer",
                  marginBottom: "15px",
                  width: "100%",
                  maxWidth: "300px"
                }}
              >
                {loading ? "⏳ Getting Location..." : "📍 Allow Location Access"}
              </button>

              <div>
                <button
                  onClick={() => {
                    setLocationStatus("denied");
                    fetchAllData();
                  }}
                  style={{
                    background: "transparent",
                    border: "none",
                    color: "#666",
                    cursor: "pointer",
                    textDecoration: "underline",
                    fontSize: "14px"
                  }}
                >
                  Continue without location
                </button>
              </div>

              {locationStatus === "denied" && (
                <div style={{
                  marginTop: "20px",
                  padding: "15px",
                  background: "#f8d7da",
                  borderRadius: "8px",
                  color: "#721c24",
                  fontSize: "14px"
                }}>
                  ⚠️ Location access was denied. Showing all centers. You can enable location
                  in your browser settings to see nearby services.
                </div>
              )}
            </div>
          ) : (
            // Show Map when location is granted or loading data
            <div className="map-wrapper">
              <PoisonMap 
                userLocation={userLocation} 
                poisonCenters={poisonCenters}
                hospitals={hospitals}
              />
            </div>
          )}
        </section>
      )}

      {/* LOADING STATE */}
      {loading && (
        <section className="hospitals-section">
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>⏳</div>
            <p>Loading emergency services...</p>
          </div>
        </section>
      )}

      {/* RESOURCES LIST */}
      {!loading && (
        <section className="hospitals-section">
          <div className="hospitals-container">
            {filteredItems.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px', width: '100%' }}>
                <div style={{ fontSize: '48px', marginBottom: '20px' }}>🔍</div>
                <p>No resources found. Please enable location services or check your connection.</p>
              </div>
            ) : (
              filteredItems.map((item) => (
                <div key={`${item.type}-${item.id}`} className="hospital-card-page">
                  <div className="card-header">
                    <div className="category-badge">
                      {item.type === "poison" ? "☠️ Poison Control" : "🏥 Hospital"}
                    </div>
                    {item.distance_km && (
                      <div className="distance-badge">
                        📍 {item.distance_km.toFixed(1)} km
                      </div>
                    )}
                  </div>

                  <div className="card-body">
                    <h3>{item.name}</h3>

                    <div className="hospital-info">
                      <div className="info-item">
                        <span className="info-label">📍 Address:</span>
                        <span>{item.address}, {item.city}, {item.state}</span>
                      </div>
                      <div className="info-item">
                        <span className="info-label">🕒 Hours:</span>
                        <span>{item.is_24_hours ? "Open 24/7" : "Check availability"}</span>
                      </div>
                      <div className="info-item">
                        <span className="info-label">📞 Phone:</span>
                        <span>{item.phone_primary || item.phone || item.emergency_phone}</span>
                      </div>
                      {item.toll_free_number && (
                        <div className="info-item">
                          <span className="info-label">📞 Toll-Free:</span>
                          <span style={{ color: 'green', fontWeight: 'bold' }}>{item.toll_free_number}</span>
                        </div>
                      )}
                    </div>

                    <div className="services-list">
                      {(item.services || item.facilities || []).slice(0, 4).map((service, idx) => (
                        <span key={idx} className="service-tag">
                          {service}
                        </span>
                      ))}
                      {item.is_verified && <span className="service-tag verified">✅ Verified</span>}
                      {item.government_affiliated && <span className="service-tag govt">🏛️ Govt</span>}
                    </div>
                  </div>

                  <div className="card-actions">
                    <a 
                      href={`tel:${item.phone_primary || item.phone || item.emergency_phone}`} 
                      className="btn-call-page"
                    >
                      📞 Call Now
                    </a>
                    {item.latitude && item.longitude && (
                      <a 
                        href={userLocation 
                          ? `https://www.google.com/maps/dir/${userLocation.latitude},${userLocation.longitude}/${item.latitude},${item.longitude}`
                          : `https://www.google.com/maps/search/?api=1&query=${item.latitude},${item.longitude}`
                        }
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn-directions-page"
                      >
                        🗺️ Directions
                      </a>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      )}

      {/* Emergency Numbers Section - Nepal */}
      <section className="emergency-numbers-section" style={{ 
        background: '#fff3cd', 
        padding: '20px', 
        margin: '20px',
        borderRadius: '12px',
        border: '2px solid #ffc107'
      }}>
        <h3 style={{ textAlign: 'center', marginBottom: '15px' }}>🚨 Nepal Emergency Numbers</h3>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '30px', flexWrap: 'wrap' }}>
          <a href="tel:102" style={{ textAlign: 'center', textDecoration: 'none', color: 'inherit' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc3545' }}>102</div>
            <div>Ambulance</div>
          </a>
          <a href="tel:1102" style={{ textAlign: 'center', textDecoration: 'none', color: 'inherit' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc3545' }}>1102</div>
            <div>NPIC Toll-Free</div>
          </a>
          <a href="tel:+977-1-4412505" style={{ textAlign: 'center', textDecoration: 'none', color: 'inherit' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc3545' }}>01-4412505</div>
            <div>Poison Center (TUTH)</div>
          </a>
          <a href="tel:100" style={{ textAlign: 'center', textDecoration: 'none', color: 'inherit' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc3545' }}>100</div>
            <div>Police</div>
          </a>
        </div>
      </section>

      <Footer />
    </>
  );
}
