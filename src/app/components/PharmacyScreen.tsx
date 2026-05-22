import { useState, useEffect, useRef } from "react";
import { MapPin, Clock, Navigation, Share2, Star, Phone, Loader2, Locate, Search } from "lucide-react";
import { motion } from "motion/react";
import L from "leaflet";
import { api } from "../../lib/api";

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

// Custom marker icons
function makeIcon(color: string): L.DivIcon {
  return L.divIcon({
    className: "",
    iconSize: [28, 36],
    iconAnchor: [14, 36],
    popupAnchor: [0, -36],
    html: `<svg width="28" height="36" viewBox="0 0 28 36" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M14 0C6.268 0 0 6.268 0 14c0 10.5 14 22 14 22s14-11.5 14-22C28 6.268 21.732 0 14 0z" fill="${color}"/>
      <circle cx="14" cy="14" r="6" fill="white" opacity="0.9"/>
    </svg>`,
  });
}

const pharmacyIcon = makeIcon("#22c55e");
const clinicIcon = makeIcon("#3b82f6");
const userIcon = L.divIcon({
  className: "",
  iconSize: [20, 20],
  iconAnchor: [10, 10],
  html: `<div style="width:20px;height:20px;border-radius:50%;background:#2563eb;border:3px solid white;box-shadow:0 0 8px rgba(37,99,235,0.5)"></div>`,
});

function LeafletMap({
  userPos,
  pharmacies,
  radiusKm,
}: {
  userPos: [number, number] | null;
  pharmacies: Pharmacy[];
  radiusKm: number;
}) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersRef = useRef<L.Layer[]>([]);

  // Initialize map once
  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    const map = L.map(mapRef.current, {
      zoomControl: false,
      scrollWheelZoom: true,
    }).setView(userPos || [14.5995, 120.9842], 14);

    L.control.zoom({ position: "topright" }).addTo(map);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map);

    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update markers when data changes
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Clear old markers
    markersRef.current.forEach((m) => map.removeLayer(m));
    markersRef.current = [];

    // User location marker
    if (userPos) {
      const um = L.marker(userPos, { icon: userIcon, zIndexOffset: 1000 })
        .addTo(map)
        .bindPopup(`<div style="text-align:center"><strong>You are here</strong></div>`);
      markersRef.current.push(um);

      // Search radius circle
      const circle = L.circle(userPos, {
        radius: radiusKm * 1000,
        color: "#3b82f6",
        fillColor: "#3b82f6",
        fillOpacity: 0.06,
        weight: 1.5,
        dashArray: "6 4",
      }).addTo(map);
      markersRef.current.push(circle);
    }

    // Pharmacy/clinic markers
    pharmacies.forEach((p) => {
      if (!p.lat || !p.lng) return;
      const icon = p.type === "pharmacy" ? pharmacyIcon : clinicIcon;
      const marker = L.marker([p.lat, p.lng], { icon })
        .addTo(map)
        .bindPopup(
          `<div style="min-width:180px;line-height:1.5">
            <div style="font-weight:600;font-size:14px">${p.name}</div>
            <div style="font-size:11px;color:#666;margin-top:2px">${p.type === "pharmacy" ? "Pharmacy" : "Clinic/Hospital"}</div>
            <div style="font-size:12px;color:#3b82f6;font-weight:500;margin-top:4px">${p.distance}</div>
            <div style="font-size:11px;color:#888;margin-top:2px">${p.address.slice(0, 80)}</div>
            <div style="margin-top:6px">
              <a href="https://www.google.com/maps/dir/?api=1&destination=${p.lat},${p.lng}" target="_blank" rel="noopener" style="display:inline-block;padding:4px 10px;background:#3b82f6;color:white;border-radius:6px;font-size:11px;text-decoration:none;font-weight:500">Directions</a>
              ${p.phone ? `<a href="tel:${p.phone}" style="display:inline-block;padding:4px 10px;background:#e5e7eb;color:#374151;border-radius:6px;font-size:11px;text-decoration:none;margin-left:4px;font-weight:500">Call</a>` : ""}
            </div>
          </div>`
        );
      markersRef.current.push(marker);
    });

    // Fit bounds
    if (pharmacies.length > 0) {
      const bounds = L.latLngBounds(
        pharmacies.map((p) => [p.lat, p.lng] as [number, number])
      );
      if (userPos) bounds.extend(userPos);
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 });
    } else if (userPos) {
      map.setView(userPos, 14);
    }
  }, [userPos, pharmacies, radiusKm]);

  return (
    <div
      ref={mapRef}
      className="w-full rounded-2xl overflow-hidden shadow-md"
      style={{ height: "clamp(280px, 45vw, 450px)" }}
    />
  );
}

function CenterOnMe({ mapRef }: { mapRef: React.MutableRefObject<L.Map | null> }) {
  return (
    <button
      onClick={() => {
        const map = mapRef.current;
        if (!map) return;
        navigator.geolocation.getCurrentPosition(
          (pos) => map.setView([pos.coords.latitude, pos.coords.longitude], 15),
          () => {},
          { timeout: 5000 }
        );
      }}
      className="absolute bottom-3 right-3 z-[1000] w-10 h-10 rounded-xl bg-white shadow-lg flex items-center justify-center hover:bg-gray-50 active:scale-95 transition-transform"
      title="Center on my location"
    >
      <Locate className="w-5 h-5 text-blue-600" />
    </button>
  );
}

interface PharmacyScreenProps {
  darkMode: boolean;
}

export function PharmacyScreen({ darkMode }: PharmacyScreenProps) {
  const [activeTab] = useState<"prescription">("prescription");
  const [pharmacies, setPharmacies] = useState<Pharmacy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [userPos, setUserPos] = useState<[number, number] | null>(null);
  const [radiusKm, setRadiusKm] = useState(10);
  const [addressName, setAddressName] = useState("Detecting your location...");

  const theme = (light: string, dark: string) => (darkMode ? dark : light);

  useEffect(() => {
    let cancelled = false;

    async function fetchPharmacies() {
      try {
        const pos = await new Promise<GeolocationPosition>((resolve, reject) => {
          if (!navigator.geolocation) reject(new Error("Geolocation not supported"));
          navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 10000, enableHighAccuracy: true });
        });

        if (cancelled) return;
        const { latitude, longitude } = pos.coords;
        setUserPos([latitude, longitude]);

        // Reverse geocode for address display
        fetch(`https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`, {
          headers: { "User-Agent": "MediGuideApp/1.0" },
        })
          .then((r) => r.json())
          .then((d) => { if (!cancelled && d.display_name) setAddressName(d.display_name.split(",").slice(0, 3).join(", ")); })
          .catch(() => {});

        const data = await api.pharmacy.nearby(latitude, longitude, radiusKm);

        if (cancelled) return;
        const mapped: Pharmacy[] = data.map((p: any) => {
          const nameRaw = p.name || "";
          const name = nameRaw.toLowerCase();
          const address = (p.address || "").toLowerCase();
          const hasOpening = Boolean(p.extratags && (p.extratags.opening_hours || p.extratags.open_hours));
          const isPharmacyType = p.type === "pharmacy" || /pharmacy|chemist|drugstore|apotek|apoteket|pharmacie/i.test(name + " " + address);
          const isClinicName = /clinic|hospital|medical|health center|healthcentre|nhs|medical center|medical centre|surgery/i.test(name + " " + address);

          // Determine display type: prefer clinic/hospital detection from name/address, otherwise use server-provided type
          const displayType: "pharmacy" | "clinic" = isClinicName && !isPharmacyType ? "clinic" : isPharmacyType ? "pharmacy" : (isClinicName ? "clinic" : (p.type === "clinic" || p.type === "hospital" ? "clinic" : "pharmacy"));

          // OTC: retail pharmacies (named as pharmacy/chemist/drugstore) and likely have opening hours
          const otcAvailable = isPharmacyType && (hasOpening || /pharmacy|chemist|drugstore|boots|cvs|walgreens|apotek/i.test(name));
          // Prescription: clinics/hospitals or pharmacies that appear to dispense (pharmacy type)
          const prescriptionAvailable = displayType === "clinic" || isPharmacyType;

          return {
            id: p.id,
            name: p.name,
            type: displayType,
            distance: p.distance,
            address: p.address,
            isOpen: p.isOpen,
            closingTime: "N/A",
            rating: 0,
            services: [],
            phone: p.phone,
            otcAvailable,
            prescriptionAvailable,
            lat: p.lat,
            lng: p.lng,
          };
        });
        setPharmacies(mapped);
      } catch {
        if (!cancelled) {
          setError("Location access needed for nearby results. Please enable location in your browser.");
          setUserPos([14.5995, 120.9842]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchPharmacies();
    return () => { cancelled = true; };
  }, [radiusKm]);

  const filtered = pharmacies.filter((p) => p.prescriptionAvailable);

  return (
    <div className={theme("bg-gray-50", "bg-gray-950")}>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8">

        {/* Page header */}
        <div className="mb-4">
          <h2 className={theme("text-gray-900", "text-white")} style={{ fontSize: "24px", fontWeight: 700 }}>Find Nearby</h2>
          <p className={`flex items-center gap-1.5 mt-1 ${theme("text-gray-500", "text-gray-400")}`} style={{ fontSize: "13px" }}>
            <MapPin className="w-3.5 h-3.5 flex-shrink-0" />
            <span className="truncate">{addressName}</span>
          </p>
          {error && <p className="mt-1 text-xs text-amber-500">{error}</p>}
        </div>

        {/* Radius selector */}
        <div className="flex items-center gap-3 mb-4">
          <span className={`text-xs ${darkMode ? "text-gray-400" : "text-gray-500"}`}>Search radius:</span>
          {[2, 5, 10, 20].map((r) => (
            <button
              key={r}
              onClick={() => { setRadiusKm(r); setLoading(true); }}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                radiusKm === r
                  ? "bg-blue-500 text-white shadow"
                  : darkMode
                    ? "bg-gray-800 text-gray-400 hover:bg-gray-700"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {r} km
            </button>
          ))}
          <span className={`ml-auto text-xs ${theme("text-gray-400", "text-gray-500")}`}>
            {loading ? "Searching..." : `${pharmacies.length} found`}
          </span>
        </div>

        <div className="grid lg:grid-cols-5 gap-6">
          {/* Left: map + legend */}
          <div className="lg:col-span-2 space-y-4">
            <div className="relative">
              <LeafletMap userPos={userPos} pharmacies={pharmacies} radiusKm={radiusKm} />
            </div>

            <button className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-500 to-teal-500 text-white flex items-center justify-center gap-2 min-h-[48px] shadow-md"
              style={{ fontSize: "14px", fontWeight: 600 }}>
              <Share2 className="w-4 h-4" />
              Send Recommendation to Pharmacist
            </button>

            {/* Legend */}
            <div className={`rounded-2xl p-4 ${theme("bg-white border border-gray-100 shadow-sm", "bg-gray-800 border border-gray-700")}`}>
              <p className={`mb-3 ${darkMode ? "text-gray-300" : "text-gray-700"}`} style={{ fontSize: "13px", fontWeight: 600 }}>Map Legend</p>
              <div className="space-y-2">
                {[
                  { color: "#2563eb", label: "Your location" },
                  { color: "#22c55e", label: "Pharmacy / Drugstore" },
                  { color: "#3b82f6", label: "Clinic / Hospital" },
                ].map((item) => (
                  <div key={item.label} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }} />
                    <span className={`${darkMode ? "text-gray-400" : "text-gray-600"}`} style={{ fontSize: "12px" }}>{item.label}</span>
                  </div>
                ))}
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full flex-shrink-0 border border-blue-400" style={{ background: "rgba(59,130,246,0.1)" }} />
                  <span className={`${darkMode ? "text-gray-400" : "text-gray-600"}`} style={{ fontSize: "12px" }}>Search radius</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right: list */}
          <div className="lg:col-span-3 space-y-4">
            {/* Tabs */}
            <div className={`flex rounded-xl p-1 ${theme("bg-gray-100", "bg-gray-800")}`}>
              <div className="flex-1">
                <div className={`py-2.5 rounded-lg text-center ${theme("bg-white text-blue-600 shadow", "bg-blue-600 text-white shadow")}`} style={{ fontSize: "13px", fontWeight: 600 }}>
                  Prescription
                </div>
              </div>
            </div>

            <div className="space-y-3">
              {loading && (
                <div className="flex flex-col items-center justify-center py-12">
                  <Loader2 className="w-6 h-6 text-blue-500 animate-spin mb-3" />
                  <p className={`text-sm ${darkMode ? "text-gray-400" : "text-gray-500"}`}>Searching nearby pharmacies...</p>
                </div>
              )}
              {!loading && filtered.map((pharmacy, i) => (
                <motion.div key={pharmacy.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}
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
                            <span className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "12px" }}>{pharmacy.address.length > 60 ? pharmacy.address.slice(0, 60) + "..." : pharmacy.address}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-1 ml-3 flex-shrink-0">
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
                      {pharmacy.rating > 0 && (
                        <div className="flex items-center gap-1">
                          <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                          <span className={`${darkMode ? "text-gray-300" : "text-gray-700"}`} style={{ fontSize: "12px", fontWeight: 600 }}>{pharmacy.rating}</span>
                        </div>
                      )}
                    </div>

                    {pharmacy.services.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mb-3">
                        {pharmacy.services.map((s) => (
                          <span key={s} className={`px-2 py-1 rounded-full text-xs ${SERVICE_COLORS[s] || SERVICE_COLORS.default}`}>{s}</span>
                        ))}
                      </div>
                    )}

                    <div className="flex gap-2">
                      <a
                        href={`https://www.google.com/maps/dir/?api=1&destination=${pharmacy.lat},${pharmacy.lng}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`flex-1 py-2.5 rounded-xl flex items-center justify-center gap-1.5 min-h-[44px] ${darkMode ? "bg-blue-600 text-white" : "bg-blue-500 text-white"}`}
                        style={{ fontSize: "13px", fontWeight: 600, textDecoration: "none" }}
                      >
                        <Navigation className="w-4 h-4" />
                        Directions
                      </a>
                      {pharmacy.phone ? (
                        <a
                          href={`tel:${pharmacy.phone}`}
                          className={`flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl min-h-[44px] ${darkMode ? "bg-gray-700 text-gray-300" : "bg-gray-100 text-gray-700"}`}
                          style={{ fontSize: "13px", fontWeight: 600, textDecoration: "none" }}
                        >
                          <Phone className="w-4 h-4" />
                          Call
                        </a>
                      ) : (
                        <button
                          className={`flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl min-h-[44px] ${darkMode ? "bg-gray-800 text-gray-600" : "bg-gray-50 text-gray-400"} cursor-not-allowed`}
                          style={{ fontSize: "13px", fontWeight: 600 }}
                          disabled
                        >
                          <Phone className="w-4 h-4" />
                          N/A
                        </button>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
              {!loading && filtered.length === 0 && !error && (
                <div className={`text-center py-12 ${darkMode ? "text-gray-500" : "text-gray-400"}`}>
                  <MapPin className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No pharmacies found within {radiusKm} km</p>
                  <button
                    onClick={() => { setRadiusKm(20); setLoading(true); }}
                    className="mt-2 text-blue-500 text-sm underline"
                  >
                    Expand to 20 km
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
