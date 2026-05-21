import { useState, useEffect, useRef } from "react";
import { MapPin, Clock, Navigation, Share2, Star, Phone, Loader2 } from "lucide-react";
import { motion } from "motion/react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import { api } from "../../lib/api";

// Fix Leaflet default marker icons (bundlers break the default paths)
const markerIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const pharmacyIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
  className: "pharmacy-marker",
});

interface Pharmacy {
  id: string;
  name: string;
  type: "pharmacy" | "clinic";
  distance: string;
  address: string;
  isOpen: boolean;
  closingTime: string;
  rating: number;
  services: string[];
  phone: string;
  otcAvailable: boolean;
  prescriptionAvailable: boolean;
  lat: number;
  lng: number;
}

const SERVICE_COLORS: Record<string, string> = {
  "24h service": "bg-purple-100 text-purple-700",
  "Home delivery": "bg-blue-100 text-blue-700",
  "Doctor consultation": "bg-teal-100 text-teal-700",
  "Prescription filling": "bg-green-100 text-green-700",
  "Emergency care": "bg-red-100 text-red-700",
  default: "bg-gray-100 text-gray-600",
};

function MapUpdater({ center, pharmacies }: { center: [number, number]; pharmacies: Pharmacy[] }) {
  const map = useMap();

  useEffect(() => {
    if (pharmacies.length > 0) {
      const bounds = L.latLngBounds(
        pharmacies.map((p) => [p.lat, p.lng] as [number, number])
      );
      bounds.extend(center);
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
    } else {
      map.setView(center, 13);
    }
  }, [center, pharmacies, map]);

  return null;
}

interface PharmacyScreenProps {
  darkMode: boolean;
}

export function PharmacyScreen({ darkMode }: PharmacyScreenProps) {
  const [activeTab, setActiveTab] = useState<"otc" | "prescription">("otc");
  const [pharmacies, setPharmacies] = useState<Pharmacy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [userPos, setUserPos] = useState<[number, number] | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchPharmacies() {
      try {
        const pos = await new Promise<GeolocationPosition>((resolve, reject) => {
          if (!navigator.geolocation) reject(new Error("Geolocation not supported"));
          navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 8000 });
        });

        if (cancelled) return;
        const { latitude, longitude } = pos.coords;
        setUserPos([latitude, longitude]);

        const data = await api.pharmacy.nearby(latitude, longitude);

        if (cancelled) return;
        const mapped: Pharmacy[] = data.map((p: any) => ({
          id: p.id,
          name: p.name,
          type: p.type,
          distance: p.distance,
          address: p.address,
          isOpen: p.isOpen,
          closingTime: "N/A",
          rating: 0,
          services: [],
          phone: p.phone,
          otcAvailable: p.type === "pharmacy",
          prescriptionAvailable: true,
          lat: p.lat,
          lng: p.lng,
        }));
        setPharmacies(mapped);
      } catch {
        if (!cancelled) {
          setError("Location access needed for nearby results");
          // Default to Manila if geolocation fails
          setUserPos([14.5995, 120.9842]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchPharmacies();
    return () => { cancelled = true; };
  }, []);

  const filtered = pharmacies.filter((p) => activeTab === "otc" ? p.otcAvailable : p.prescriptionAvailable);
  const mapCenter = userPos || [14.5995, 120.9842];

  return (
    <div className={`${darkMode ? "bg-gray-950" : "bg-gray-50"}`}>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8">

        {/* Page header */}
        <div className="mb-6">
          <h2 className={`${darkMode ? "text-white" : "text-gray-900"}`} style={{ fontSize: "24px", fontWeight: 700 }}>Find Nearby</h2>
          <p className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "14px" }}>
            {loading ? "Searching nearby pharmacies..." : "Pharmacies and clinics near your location"}
          </p>
          {error && (
            <p className="mt-1 text-xs text-amber-500">{error}</p>
          )}
        </div>

        <div className="grid lg:grid-cols-5 gap-6">
          {/* Left: map + filters */}
          <div className="lg:col-span-2 space-y-4">
            {/* Real Leaflet map */}
            <div className="rounded-2xl overflow-hidden" style={{ height: "clamp(220px, 30vw, 320px)" }}>
              {userPos ? (
                <MapContainer
                  center={mapCenter}
                  zoom={13}
                  scrollWheelZoom={true}
                  style={{ height: "100%", width: "100%" }}
                >
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  <MapUpdater center={mapCenter} pharmacies={pharmacies} />

                  {/* User location marker */}
                  <Marker position={userPos} icon={markerIcon}>
                    <Popup><strong>You are here</strong></Popup>
                  </Marker>

                  {/* Pharmacy markers */}
                  {pharmacies.map((p) => (
                    <Marker key={p.id} position={[p.lat, p.lng]} icon={pharmacyIcon}>
                      <Popup>
                        <div style={{ minWidth: 150 }}>
                          <strong>{p.name}</strong>
                          <br />
                          <span style={{ fontSize: 12, color: "#666" }}>{p.type === "pharmacy" ? "Pharmacy" : "Clinic"}</span>
                          <br />
                          <span style={{ fontSize: 12 }}>{p.distance}</span>
                          {p.address && (
                            <>
                              <br />
                              <span style={{ fontSize: 11, color: "#888" }}>{p.address.slice(0, 60)}</span>
                            </>
                          )}
                        </div>
                      </Popup>
                    </Marker>
                  ))}
                </MapContainer>
              ) : (
                <div className={`w-full h-full flex items-center justify-center ${darkMode ? "bg-gray-800" : "bg-gray-100"}`}>
                  <div className="text-center">
                    <Loader2 className="w-6 h-6 text-blue-500 animate-spin mx-auto mb-2" />
                    <p className={`text-sm ${darkMode ? "text-gray-400" : "text-gray-500"}`}>Loading map...</p>
                  </div>
                </div>
              )}
            </div>

            <button className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-500 to-teal-500 text-white flex items-center justify-center gap-2 min-h-[48px] shadow-md"
              style={{ fontSize: "14px", fontWeight: 600 }}>
              <Share2 className="w-4 h-4" />
              Send Recommendation to Pharmacist
            </button>

            {/* Legend */}
            <div className={`rounded-2xl p-4 ${darkMode ? "bg-gray-800 border border-gray-700" : "bg-white border border-gray-100 shadow-sm"}`}>
              <p className={`mb-3 ${darkMode ? "text-gray-300" : "text-gray-700"}`} style={{ fontSize: "13px", fontWeight: 600 }}>Map Legend</p>
              <div className="space-y-2">
                {[
                  { color: "#22c55e", label: "Pharmacy (OTC available)" },
                  { color: "#3b82f6", label: "Clinic (consultation)" },
                  { color: "#a855f7", label: "Extended hours" },
                  { color: "#6b7280", label: "Currently closed" },
                ].map((item) => (
                  <div key={item.label} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }} />
                    <span className={`${darkMode ? "text-gray-400" : "text-gray-600"}`} style={{ fontSize: "12px" }}>{item.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right: list */}
          <div className="lg:col-span-3 space-y-4">
            {/* Tabs */}
            <div className={`flex rounded-xl p-1 ${darkMode ? "bg-gray-800" : "bg-gray-100"}`}>
              {[{ key: "otc", label: "Over-the-Counter" }, { key: "prescription", label: "Get Prescription" }].map((tab) => (
                <button key={tab.key} onClick={() => setActiveTab(tab.key as "otc" | "prescription")}
                  className={`flex-1 py-2.5 rounded-lg transition-all min-h-[44px] ${
                    activeTab === tab.key ? darkMode ? "bg-blue-600 text-white shadow" : "bg-white text-blue-600 shadow" : darkMode ? "text-gray-400" : "text-gray-500"
                  }`}
                  style={{ fontSize: "13px", fontWeight: 600 }}>
                  {tab.label}
                </button>
              ))}
            </div>

            <div className="space-y-3">
              {loading && (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
                </div>
              )}
              {!loading && filtered.map((pharmacy, i) => (
                <motion.div key={pharmacy.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}
                  className={`rounded-2xl overflow-hidden ${darkMode ? "bg-gray-800 border border-gray-700" : "bg-white border border-gray-100 shadow-sm"}`}>
                  <div className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-start gap-3">
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${pharmacy.type === "pharmacy" ? darkMode ? "bg-green-900/40" : "bg-green-50" : darkMode ? "bg-blue-900/40" : "bg-blue-50"}`}>
                          <span style={{ fontSize: "20px" }}>{pharmacy.type === "pharmacy" ? "💊" : "🏥"}</span>
                        </div>
                        <div>
                          <p className={`${darkMode ? "text-white" : "text-gray-900"}`} style={{ fontSize: "15px", fontWeight: 600 }}>{pharmacy.name}</p>
                          <div className="flex items-center gap-1 mt-0.5">
                            <MapPin className={`w-3 h-3 ${darkMode ? "text-gray-500" : "text-gray-400"}`} />
                            <span className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "12px" }}>{pharmacy.address}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-1 ml-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${pharmacy.isOpen ? darkMode ? "bg-green-900/40 text-green-400" : "bg-green-50 text-green-600" : darkMode ? "bg-gray-700 text-gray-400" : "bg-gray-100 text-gray-500"}`}>
                          {pharmacy.isOpen ? "Open Now" : "Closed"}
                        </span>
                        <span className={`${darkMode ? "text-blue-400" : "text-blue-500"}`} style={{ fontSize: "13px", fontWeight: 600 }}>{pharmacy.distance}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 mb-3">
                      <div className="flex items-center gap-1">
                        <Clock className={`w-3 h-3 ${darkMode ? "text-gray-500" : "text-gray-400"}`} />
                        <span className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "12px" }}>
                          {pharmacy.isOpen ? `Closes ${pharmacy.closingTime}` : pharmacy.closingTime}
                        </span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                        <span className={`${darkMode ? "text-gray-300" : "text-gray-700"}`} style={{ fontSize: "12px", fontWeight: 600 }}>{pharmacy.rating}</span>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-1.5 mb-3">
                      {pharmacy.services.map((s) => (
                        <span key={s} className={`px-2 py-1 rounded-full text-xs ${SERVICE_COLORS[s] || SERVICE_COLORS.default}`}>{s}</span>
                      ))}
                    </div>

                    <div className="flex gap-2">
                      <button className={`flex-1 py-2.5 rounded-xl flex items-center justify-center gap-1.5 min-h-[44px] ${darkMode ? "bg-blue-600 text-white" : "bg-blue-500 text-white"}`}
                        style={{ fontSize: "13px", fontWeight: 600 }}>
                        <Navigation className="w-4 h-4" />
                        Directions
                      </button>
                      <button className={`flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl min-h-[44px] ${darkMode ? "bg-gray-700 text-gray-300" : "bg-gray-100 text-gray-700"}`}
                        style={{ fontSize: "13px", fontWeight: 600 }}>
                        <Phone className="w-4 h-4" />
                        Call
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
              {!loading && filtered.length === 0 && !error && (
                <div className={`text-center py-12 ${darkMode ? "text-gray-500" : "text-gray-400"}`}>
                  <MapPin className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No pharmacies found nearby</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
