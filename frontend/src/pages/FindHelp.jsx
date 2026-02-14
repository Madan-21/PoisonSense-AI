import React, { useState, useEffect, useMemo } from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import PoisonMap from "../components/PoisonMap";
import { centerApi } from "../api/centerApi";
import { getErrorMessage } from "../utils/errorHandler";
import "../styles/FindHelp.css";

export default function FindHelp() {
  const [filterType, setFilterType] = useState("all");
  const [viewType, setViewType] = useState("map");
  const [userLocation, setUserLocation] = useState(null);

  const [hospitals, setHospitals] = useState([]);
  const [poisonCenters, setPoisonCenters] = useState([]);
  const [toxicologyLabs, setToxicologyLabs] = useState([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [locationStatus, setLocationStatus] = useState("idle"); // idle, loading, granted, denied
  const [showLocationModal, setShowLocationModal] = useState(true);

  const [selectedItem, setSelectedItem] = useState(null);

  // ---------- helpers for the new UI ----------
  const kmToMiles = (km) => km * 0.621371;

  const getTypeLabel = (t) =>
    t === "poison"
      ? "Poison Control"
      : t === "lab"
        ? "Toxicology Lab"
        : "Emergency Room";

  const getTypeIcon = (t) =>
    t === "poison" ? "🚑" : t === "lab" ? "🧪" : "🏥";

  const getIconClass = (t) =>
    t === "poison" ? "icon-poison" : t === "lab" ? "icon-lab" : "icon-hospital";

  const getPhone = (item) =>
    item.phone_primary || item.phone || item.emergency_phone || "";

  const getFullAddress = (item) => {
    const parts = [];
    if (item.address) parts.push(item.address);
    if (item.city) parts.push(item.city);
    if (item.state) parts.push(item.state);
    return parts.join(", ");
  };

  // ---------- location + fetch ----------
  const fetchNearbyData = async (latitude, longitude) => {
    setLoading(true);
    try {
      const [hospitalsRes, centersRes, labsRes] = await Promise.all([
        centerApi.getNearbyHospitals(latitude, longitude, {
          radiusKm: 500,
          limit: 20,
        }),
        centerApi.getNearbyPoisonCenters(latitude, longitude, {
          radiusKm: 1000,
          limit: 20,
        }),
        centerApi.getNearbyLabs(latitude, longitude, 500),
      ]);

      const hospitalsData = hospitalsRes?.hospitals || hospitalsRes || [];
      const centersData = centersRes?.centers || centersRes || [];
      const labsData = labsRes?.labs || labsRes || [];

      setHospitals(hospitalsData);
      setPoisonCenters(centersData);
      setToxicologyLabs(labsData);

      if (
        hospitalsData.length === 0 &&
        centersData.length === 0 &&
        labsData.length === 0
      ) {
        await fetchAllData();
      }
    } catch (err) {
      console.error("Error fetching nearby data:", err);
      setError(
        getErrorMessage(
          err,
          "Failed to fetch nearby resources. Loading all centers...",
        ),
      );
      await fetchAllData();
    } finally {
      setLoading(false);
    }
  };

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [hospitalsRes, centersRes, labsRes] = await Promise.all([
        centerApi.getAllHospitals(),
        centerApi.getAllPoisonCenters(),
        centerApi.getNearbyLabs(27.7172, 85.324, 5000), // Default Nepal center with large radius
      ]);

      setHospitals(Array.isArray(hospitalsRes) ? hospitalsRes : []);
      setPoisonCenters(Array.isArray(centersRes) ? centersRes : []);
      setToxicologyLabs(
        Array.isArray(labsRes?.labs || labsRes) ? labsRes?.labs || labsRes : [],
      );
    } catch (err) {
      console.error("Error fetching all data:", err);
      setError(
        getErrorMessage(
          err,
          "Failed to load emergency services. Please check if the backend is running.",
        ),
      );
    } finally {
      setLoading(false);
    }
  };

  const getLocationAndFetchData = async () => {
    setLocationStatus("loading");
    setError(null);

    // Try stored location
    const storedLocation = localStorage.getItem("userLocation");
    if (storedLocation) {
      try {
        const location = JSON.parse(storedLocation);
        setUserLocation(location);
        setLocationStatus("granted");
        setShowLocationModal(false);
        await fetchNearbyData(location.latitude, location.longitude);
        return;
      } catch (e) {
        console.log("Error parsing stored location:", e);
      }
    }

    if (!navigator.geolocation) {
      setError("Geolocation is not supported by your browser");
      setLocationStatus("denied");
      setShowLocationModal(false);
      fetchAllData();
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        const loc = { latitude, longitude };
        setUserLocation(loc);
        localStorage.setItem("userLocation", JSON.stringify(loc));
        setLocationStatus("granted");
        setShowLocationModal(false);
        setError(null);
        await fetchNearbyData(latitude, longitude);
      },
      (geoErr) => {
        console.error("Location error:", geoErr);
        setLocationStatus("denied");
        setShowLocationModal(false);
        setError("Location access denied. Showing all centers.");
        fetchAllData();
      },
      { enableHighAccuracy: true, timeout: 10000 },
    );
  };

  // Auto-load on mount
  useEffect(() => {
    const storedLocation = localStorage.getItem("userLocation");
    if (storedLocation) {
      try {
        const location = JSON.parse(storedLocation);
        setUserLocation(location);
        setLocationStatus("granted");
        setShowLocationModal(false);
        setError(null);
        fetchNearbyData(location.latitude, location.longitude);
      } catch (e) {
        console.log("Error parsing stored location:", e);
        // Load all data as fallback
        fetchAllData();
      }
    } else {
      // No stored location - load all data by default
      fetchAllData();
    }
  }, []);

  // ---------- filtered items ----------
  const filteredItems = useMemo(() => {
    let items = [];

    if (filterType === "all" || filterType === "poison") {
      items = [
        ...items,
        ...poisonCenters.map((c) => ({ ...c, type: "poison" })),
      ];
    }
    if (filterType === "all" || filterType === "urgent") {
      items = [...items, ...hospitals.map((h) => ({ ...h, type: "hospital" }))];
    }
    if (filterType === "all" || filterType === "labs") {
      items = [...items, ...toxicologyLabs.map((l) => ({ ...l, type: "lab" }))];
    }

    return items;
  }, [filterType, poisonCenters, hospitals, toxicologyLabs]);

  const totalCount =
    poisonCenters.length + hospitals.length + toxicologyLabs.length;

  return (
    <>
      <Navbar />

      {/* Hero Section */}
      <div className="findhelp-hero">
        <h1>Find Nearby Help</h1>
        <p>Locate emergency rooms and poison control centers in your area</p>
      </div>

      {/* Location Status Card */}
      <div className="location-status-card">
        <div className="location-status-content">
          <div className="status-icon">
            {locationStatus === "loading"
              ? "⏳"
              : locationStatus === "granted"
                ? "✅"
                : "📍"}
          </div>

          <div className="status-text">
            <h3>
              {locationStatus === "granted"
                ? "Location Enabled"
                : locationStatus === "loading"
                  ? "Detecting Location..."
                  : "Enable Location Access"}
            </h3>
            <p>
              {locationStatus === "granted"
                ? `Showing facilities near you`
                : "We need your location to find the nearest emergency services"}
            </p>
          </div>

          {locationStatus !== "granted" && (
            <button
              className="enable-location-btn"
              onClick={getLocationAndFetchData}
              disabled={loading}
            >
              {loading ? "Loading..." : "Enable Location"}
            </button>
          )}
        </div>

        {error && locationStatus !== "granted" && (
          <div className="error-message">⚠️ {error}</div>
        )}
      </div>

      {/* Filters & View Options */}
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
            All ({totalCount})
          </button>
          <button
            className={`filter-btn ${filterType === "poison" ? "active" : ""}`}
            onClick={() => setFilterType("poison")}
          >
            🚑 Poison Control ({poisonCenters.length})
          </button>
          <button
            className={`filter-btn ${filterType === "urgent" ? "active" : ""}`}
            onClick={() => setFilterType("urgent")}
          >
            🏥 Hospitals ({hospitals.length})
          </button>
          <button
            className={`filter-btn ${filterType === "labs" ? "active" : ""}`}
            onClick={() => setFilterType("labs")}
          >
            🧪 Toxicology Labs ({toxicologyLabs.length})
          </button>
        </div>
      </section>

      {/* MAP VIEW */}
      {viewType === "map" && (
        <section className="map-view-section">
          {showLocationModal && locationStatus !== "granted" ? (
            <div
              style={{
                background: "linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
                borderRadius: "16px",
                padding: "40px",
                textAlign: "center",
                maxWidth: "500px",
                margin: "20px auto",
                boxShadow: "0 4px 20px rgba(0,0,0,0.1)",
              }}
            >
              <div style={{ fontSize: "64px", marginBottom: "20px" }}>📍</div>
              <h2 style={{ marginBottom: "15px", color: "#333" }}>
                Enable Location Services
              </h2>
              <p
                style={{
                  color: "#666",
                  marginBottom: "25px",
                  lineHeight: "1.6",
                }}
              >
                To show emergency services near you on the map, we need access
                to your location. This helps us find the closest hospitals and
                poison control centers.
              </p>

              <div
                style={{
                  background: "#fff3cd",
                  padding: "15px",
                  borderRadius: "8px",
                  marginBottom: "25px",
                  fontSize: "14px",
                  color: "#856404",
                }}
              >
                <strong>🔒 Privacy Note:</strong> Your location is only used to
                find nearby services and is not stored or shared with third
                parties.
              </div>

              <button
                onClick={getLocationAndFetchData}
                disabled={locationStatus === "loading"}
                style={{
                  background:
                    "linear-gradient(135deg, #28a745 0%, #1a5f2a 100%)",
                  color: "white",
                  border: "none",
                  padding: "15px 40px",
                  borderRadius: "30px",
                  fontSize: "18px",
                  fontWeight: "bold",
                  cursor:
                    locationStatus === "loading" ? "not-allowed" : "pointer",
                  marginBottom: "15px",
                  width: "100%",
                  maxWidth: "300px",
                }}
              >
                {locationStatus === "loading"
                  ? "⏳ Getting Location..."
                  : "📍 Allow Location Access"}
              </button>

              <div>
                <button
                  onClick={() => {
                    setShowLocationModal(false);
                    setLocationStatus("denied");
                    fetchAllData();
                  }}
                  style={{
                    background: "transparent",
                    border: "none",
                    color: "#666",
                    cursor: "pointer",
                    textDecoration: "underline",
                    fontSize: "14px",
                  }}
                >
                  Continue without location
                </button>
              </div>

              {error && (
                <div
                  style={{
                    marginTop: "20px",
                    padding: "15px",
                    background: "#f8d7da",
                    borderRadius: "8px",
                    color: "#721c24",
                    fontSize: "14px",
                  }}
                >
                  ⚠️ {error}
                </div>
              )}
            </div>
          ) : (
            <div className="map-wrapper">
              <PoisonMap
                userLocation={userLocation}
                poisonCenters={poisonCenters}
                hospitals={hospitals}
                toxicologyLabs={toxicologyLabs}
              />
            </div>
          )}
        </section>
      )}

      {/* LOADING */}
      {loading && (
        <section className="hospitals-section">
          <div style={{ textAlign: "center", padding: "40px" }}>
            <div style={{ fontSize: "48px", marginBottom: "20px" }}>⏳</div>
            <p>Loading emergency services...</p>
          </div>
        </section>
      )}

      {/* LIST VIEW (and always show list below map if you want; currently shows when not loading) */}
      {!loading && (
        <section className="hospitals-section">
          <div className="findhelp-results">
            {filteredItems.length === 0 ? (
              <div
                style={{ textAlign: "center", padding: "40px", width: "100%" }}
              >
                <div style={{ fontSize: "48px", marginBottom: "20px" }}>🔍</div>
                <p>
                  No resources found. Please enable location services or check
                  your connection.
                </p>
              </div>
            ) : (
              filteredItems.map((item) => {
                const phone = getPhone(item);
                const isRecommended = !!(
                  item.is_verified || item.government_affiliated
                );

                const directionsUrl =
                  item.latitude && item.longitude
                    ? userLocation
                      ? `https://www.google.com/maps/dir/${userLocation.latitude},${userLocation.longitude}/${item.latitude},${item.longitude}`
                      : `https://www.google.com/maps/search/?api=1&query=${item.latitude},${item.longitude}`
                    : null;

                return (
                  <div
                    key={`${item.type}-${item.id}`}
                    className="resource-card"
                  >
                    {isRecommended && (
                      <div className="recommended-badge">⭐ RECOMMENDED</div>
                    )}

                    <div className="resource-card-top">
                      <div className="resource-card-main">
                        <div
                          className={`resource-icon ${getIconClass(item.type)}`}
                        >
                          {getTypeIcon(item.type)}
                        </div>

                        <div style={{ minWidth: 0, width: "100%" }}>
                          <h3 className="resource-title">{item.name}</h3>

                          <div className="resource-meta">
                            <span className="meta-pill">
                              {getTypeLabel(item.type)}
                            </span>

                            {item.distance_km != null && (
                              <>
                                <span className="dot" />
                                <span className="meta-pill">
                                  {kmToMiles(item.distance_km).toFixed(1)} miles
                                </span>
                              </>
                            )}

                            {item.rating != null && (
                              <>
                                <span className="dot" />
                                <span className="meta-pill">
                                  ⭐ {Number(item.rating).toFixed(1)}
                                </span>
                              </>
                            )}
                          </div>

                          <div className="resource-lines">
                            <div className="line">
                              <span className="label">📍</span>
                              <span
                                style={{
                                  overflow: "hidden",
                                  textOverflow: "ellipsis",
                                }}
                              >
                                {getFullAddress(item) || "N/A"}
                              </span>
                            </div>

                            <div className="line">
                              <span className="label">📞</span>
                              <span
                                style={{ color: "#2563eb", fontWeight: 800 }}
                              >
                                {phone || "N/A"}
                              </span>
                              {item.toll_free_number && (
                                <span
                                  style={{
                                    marginLeft: 10,
                                    fontWeight: 800,
                                    color: "#15803d",
                                  }}
                                >
                                  Toll-Free: {item.toll_free_number}
                                </span>
                              )}
                            </div>

                            <div className="line">
                              <span className="label">🕒</span>
                              <span>
                                {item.is_24_hours ? (
                                  <>
                                    24/7{" "}
                                    <span className="open-pill">Open Now</span>
                                  </>
                                ) : (
                                  "Check availability"
                                )}
                              </span>
                            </div>
                          </div>

                          <div className="services-row">
                            {(item.services || item.facilities || [])
                              .slice(0, 3)
                              .map((s, idx) => (
                                <span key={idx} className="tag">
                                  {s}
                                </span>
                              ))}
                            {(item.antidotes_available || [])
                              .slice(0, 3)
                              .map((a, idx) => (
                                <span key={`ant-${idx}`} className="tag" style={{ background: "#d4edda", color: "#155724" }}>
                                  💊 {a}
                                </span>
                              ))}
                            {item.is_verified && (
                              <span className="tag verified">✅ Verified</span>
                            )}
                            {item.government_affiliated && (
                              <span className="tag govt">🏛️ Govt</span>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="resource-actions">
                        <a
                          href={phone ? `tel:${phone}` : "#"}
                          className="action-btn btn-call"
                          onClick={(e) => !phone && e.preventDefault()}
                        >
                          📞 Call Now
                        </a>

                        {directionsUrl && (
                          <a
                            href={directionsUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="action-btn btn-dir"
                          >
                            🧭 Directions
                          </a>
                        )}

                        <button
                          className="action-btn btn-details"
                          onClick={() => setSelectedItem(item)}
                          type="button"
                        >
                          ℹ️ Details
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </section>
      )}

      {/* DETAILS MODAL */}
      {selectedItem && (
        <div
          onClick={() => setSelectedItem(null)}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.45)",
            display: "grid",
            placeItems: "center",
            zIndex: 9999,
            padding: 16,
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              width: "min(700px, 96vw)",
              background: "#fff",
              borderRadius: 14,
              padding: 18,
              boxShadow: "0 20px 60px rgba(0,0,0,0.25)",
            }}
          >
            <h2 style={{ margin: 0 }}>{selectedItem.name}</h2>
            <p style={{ color: "#64748b", marginTop: 6 }}>
              {getFullAddress(selectedItem) || "N/A"}
            </p>

            <div style={{ display: "grid", gap: 8, marginTop: 12 }}>
              <div>
                <b>Type:</b> {getTypeLabel(selectedItem.type)}
              </div>
              <div>
                <b>Phone:</b> {getPhone(selectedItem) || "N/A"}
              </div>
              {selectedItem.toll_free_number && (
                <div>
                  <b>Toll-Free:</b> {selectedItem.toll_free_number}
                </div>
              )}
              <div>
                <b>Hours:</b>{" "}
                {selectedItem.is_24_hours ? "Open 24/7" : "Check availability"}
              </div>
              {Array.isArray(
                selectedItem.services || selectedItem.facilities,
              ) && (
                <div>
                  <b>Services / Facilities:</b>{" "}
                  {(selectedItem.services || selectedItem.facilities).join(
                    ", ",
                  )}
                </div>
              )}
              {Array.isArray(selectedItem.antidotes_available) &&
                selectedItem.antidotes_available.length > 0 && (
                  <div>
                    <b>💊 Antidotes Available:</b>{" "}
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 6 }}>
                      {selectedItem.antidotes_available.map((a, idx) => (
                        <span
                          key={idx}
                          style={{
                            background: "#d4edda",
                            color: "#155724",
                            padding: "4px 10px",
                            borderRadius: 20,
                            fontSize: 13,
                            fontWeight: 600,
                          }}
                        >
                          {a}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              {Array.isArray(selectedItem.toxicology_tests) &&
                selectedItem.toxicology_tests.length > 0 && (
                  <div>
                    <b>🧪 Toxicology Tests:</b>{" "}
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 6 }}>
                      {selectedItem.toxicology_tests.map((t, idx) => (
                        <span
                          key={idx}
                          style={{
                            background: "#e8f4fd",
                            color: "#0c5460",
                            padding: "4px 10px",
                            borderRadius: 20,
                            fontSize: 13,
                            fontWeight: 600,
                          }}
                        >
                          {typeof t === "object" ? t.name : t}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              {selectedItem.email && (
                <div>
                  <b>📧 Email:</b> {selectedItem.email}
                </div>
              )}
              {selectedItem.website && (
                <div>
                  <b>🌐 Website:</b>{" "}
                  <a href={selectedItem.website} target="_blank" rel="noopener noreferrer" style={{ color: "#2563eb" }}>
                    {selectedItem.website}
                  </a>
                </div>
              )}
            </div>

            <div
              style={{
                display: "flex",
                justifyContent: "flex-end",
                marginTop: 16,
              }}
            >
              <button
                className="action-btn btn-details"
                onClick={() => setSelectedItem(null)}
                type="button"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Nepal Emergency Numbers */}
      <section
        className="emergency-numbers-section"
        style={{
          background: "#fff3cd",
          padding: "20px",
          margin: "20px",
          borderRadius: "12px",
          border: "2px solid #ffc107",
        }}
      >
        <h3 style={{ textAlign: "center", marginBottom: "15px" }}>
          🚨 Nepal Emergency Numbers
        </h3>
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: "30px",
            flexWrap: "wrap",
          }}
        >
          <a
            href="tel:102"
            style={{
              textAlign: "center",
              textDecoration: "none",
              color: "inherit",
            }}
          >
            <div
              style={{ fontSize: "24px", fontWeight: "bold", color: "#dc3545" }}
            >
              102
            </div>
            <div>Ambulance</div>
          </a>
          <a
            href="tel:1102"
            style={{
              textAlign: "center",
              textDecoration: "none",
              color: "inherit",
            }}
          >
            <div
              style={{ fontSize: "24px", fontWeight: "bold", color: "#dc3545" }}
            >
              1102
            </div>
            <div>NPIC Toll-Free</div>
          </a>
          <a
            href="tel:+977-1-4412505"
            style={{
              textAlign: "center",
              textDecoration: "none",
              color: "inherit",
            }}
          >
            <div
              style={{ fontSize: "24px", fontWeight: "bold", color: "#dc3545" }}
            >
              01-4412505
            </div>
            <div>Poison Center (TUTH)</div>
          </a>
          <a
            href="tel:100"
            style={{
              textAlign: "center",
              textDecoration: "none",
              color: "inherit",
            }}
          >
            <div
              style={{ fontSize: "24px", fontWeight: "bold", color: "#dc3545" }}
            >
              100
            </div>
            <div>Police</div>
          </a>
        </div>
      </section>

      <Footer />
    </>
  );
}
