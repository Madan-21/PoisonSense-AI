import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";

// Fix for default markers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
});

// Custom icons
const userIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

const poisonCenterIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

const hospitalIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

// Component to recenter map when user location changes
function RecenterMap({ position }) {
  const map = useMap();
  useEffect(() => {
    if (position) {
      map.setView(position, 10);
    }
  }, [position, map]);
  return null;
}

export default function PoisonMap({ userLocation, poisonCenters = [], hospitals = [] }) {
  // Default center (Delhi, India - where most poison centers are)
  const defaultCenter = [28.6139, 77.2090];
  
  const center = userLocation 
    ? [userLocation.latitude, userLocation.longitude]
    : defaultCenter;

  return (
    <MapContainer
      center={center}
      zoom={userLocation ? 10 : 5}
      style={{ height: "100%", width: "100%", minHeight: "400px" }}
      className="leaflet-container"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      <RecenterMap position={userLocation ? [userLocation.latitude, userLocation.longitude] : null} />
      
      {/* User location marker */}
      {userLocation && (
        <Marker position={[userLocation.latitude, userLocation.longitude]} icon={userIcon}>
          <Popup>
            <div>
              <h4>📍 Your Location</h4>
              <p>Lat: {userLocation.latitude.toFixed(4)}</p>
              <p>Lng: {userLocation.longitude.toFixed(4)}</p>
            </div>
          </Popup>
        </Marker>
      )}
      
      {/* Poison Centers markers */}
      {poisonCenters.map((center) => (
        center.latitude && center.longitude && (
          <Marker 
            key={`center-${center.id}`} 
            position={[center.latitude, center.longitude]}
            icon={poisonCenterIcon}
          >
            <Popup>
              <div style={{ minWidth: '200px' }}>
                <h4 style={{ color: '#dc3545', marginBottom: '5px' }}>☠️ {center.name}</h4>
                <p style={{ margin: '3px 0' }}><strong>📍</strong> {center.address}, {center.city}</p>
                <p style={{ margin: '3px 0' }}><strong>📞</strong> {center.phone_primary || center.phone}</p>
                {center.toll_free_number && (
                  <p style={{ margin: '3px 0', color: 'green' }}><strong>📞 Toll-Free:</strong> {center.toll_free_number}</p>
                )}
                <p style={{ margin: '3px 0' }}><strong>🕒</strong> {center.is_24_hours ? "Open 24/7" : "Limited Hours"}</p>
                {center.distance_km && (
                  <p style={{ margin: '3px 0' }}><strong>📏</strong> {center.distance_km.toFixed(1)} km away</p>
                )}
                <div style={{ display: 'flex', gap: '5px', marginTop: '10px' }}>
                  <a 
                    href={`tel:${center.phone_primary || center.phone}`} 
                    style={{ 
                      padding: '5px 10px', 
                      background: '#dc3545', 
                      color: 'white', 
                      borderRadius: '5px',
                      textDecoration: 'none',
                      fontSize: '12px'
                    }}
                  >
                    📞 Call
                  </a>
                  <a 
                    href={userLocation 
                      ? `https://www.google.com/maps/dir/${userLocation.latitude},${userLocation.longitude}/${center.latitude},${center.longitude}`
                      : `https://www.google.com/maps/search/?api=1&query=${center.latitude},${center.longitude}`
                    }
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ 
                      padding: '5px 10px', 
                      background: '#28a745', 
                      color: 'white', 
                      borderRadius: '5px',
                      textDecoration: 'none',
                      fontSize: '12px'
                    }}
                  >
                    �️ Directions
                  </a>
                </div>
              </div>
            </Popup>
          </Marker>
        )
      ))}
      
      {/* Hospital markers */}
      {hospitals.map((hospital) => (
        hospital.latitude && hospital.longitude && (
          <Marker 
            key={`hospital-${hospital.id}`} 
            position={[hospital.latitude, hospital.longitude]}
            icon={hospitalIcon}
          >
            <Popup>
              <div style={{ minWidth: '200px' }}>
                <h4 style={{ color: '#28a745', marginBottom: '5px' }}>🏥 {hospital.name}</h4>
                <p style={{ margin: '3px 0' }}><strong>📍</strong> {hospital.address}, {hospital.city}</p>
                <p style={{ margin: '3px 0' }}><strong>📞</strong> {hospital.phone || hospital.emergency_phone}</p>
                <p style={{ margin: '3px 0' }}><strong>🕒</strong> {hospital.is_24_hours ? "Open 24/7" : "Limited Hours"}</p>
                {hospital.distance_km && (
                  <p style={{ margin: '3px 0' }}><strong>📏</strong> {hospital.distance_km.toFixed(1)} km away</p>
                )}
                {hospital.antidotes_available && hospital.antidotes_available.length > 0 && (
                  <p style={{ margin: '3px 0', fontSize: '12px' }}>
                    <strong>💊</strong> {hospital.antidotes_available.slice(0, 3).join(", ")}
                  </p>
                )}
                <div style={{ display: 'flex', gap: '5px', marginTop: '10px' }}>
                  <a 
                    href={`tel:${hospital.emergency_phone || hospital.phone}`} 
                    style={{ 
                      padding: '5px 10px', 
                      background: '#dc3545', 
                      color: 'white', 
                      borderRadius: '5px',
                      textDecoration: 'none',
                      fontSize: '12px'
                    }}
                  >
                    📞 Call
                  </a>
                  <a 
                    href={userLocation 
                      ? `https://www.google.com/maps/dir/${userLocation.latitude},${userLocation.longitude}/${hospital.latitude},${hospital.longitude}`
                      : `https://www.google.com/maps/search/?api=1&query=${hospital.latitude},${hospital.longitude}`
                    }
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ 
                      padding: '5px 10px', 
                      background: '#28a745', 
                      color: 'white', 
                      borderRadius: '5px',
                      textDecoration: 'none',
                      fontSize: '12px'
                    }}
                  >
                    �️ Directions
                  </a>
                </div>
              </div>
            </Popup>
          </Marker>
        )
      ))}
    </MapContainer>
  );
}
