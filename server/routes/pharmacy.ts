import { Router, Request, Response } from "express";
import { fetch as undiciFetch } from "undici";
import { spawn } from "child_process";
import path from "path";

const router = Router();

function haversineKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function formatDistance(km: number): string {
  return km < 1 ? `${Math.round(km * 1000)} m` : `${km.toFixed(1)} km`;
}

function parseResults(raw: any[], lat: number, lng: number, radiusKm: number) {
  const seen = new Set<string>();
  return raw
    .filter((el: any) => {
      if (!el.lat || !el.lon) return false;
      const key = el.lat + "," + el.lon;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    })
    .map((el: any) => {
      const elLat = parseFloat(el.lat);
      const elLng = parseFloat(el.lon);
      const dist = haversineKm(lat, lng, elLat, elLng);
      const cls = el.class || "";
      const typ = el.type || "";
      const isPharmacy = cls === "pharmacy" || typ === "pharmacy" || typ === "chemist";
      const isHospital = cls === "hospital" || typ === "hospital";
      let placeType: "pharmacy" | "clinic" = "pharmacy";
      if (isHospital || cls === "clinic" || typ === "clinic") placeType = "clinic";

      return {
        id: String(el.osm_id),
        name: el.name || "Unknown",
        type: placeType,
        distance: formatDistance(dist),
        distanceKm: dist,
        address: el.display_name || "Address not available",
        lat: elLat,
        lng: elLng,
        phone: el.extratags?.phone || el.extratags?.["contact:phone"] || "",
        isOpen: true,
      };
    })
    .filter((p: any) => p.distanceKm <= radiusKm)
    .sort((a: any, b: any) => a.distanceKm - b.distanceKm)
    .slice(0, 50);
}

async function fetchNominatim(url: string): Promise<any[]> {
  const response = await undiciFetch(url, {
    headers: { "User-Agent": "MediGuideApp/1.0" },
  });
  if (!response.ok) return [];
  const data = await response.json();
  return Array.isArray(data) ? data : [];
}

async function fetchPharmacies(lat: number, lng: number, radiusKm: number): Promise<any[]> {
  // Search for multiple types in parallel
  const queries = [
    "pharmacy",
    "drugstore",
    "botica",
    "hospital",
    "clinic",
    "medical+center",
  ];

  // Overpass API is more accurate for POI searches — try it first
  const overpassResults = await fetchFromOverpass(lat, lng, radiusKm * 1000);
  if (overpassResults.length > 0) return overpassResults;

  // Fallback to Nominatim with multiple queries
  const viewbox = [
    (lng - radiusKm * 1.5 / 111).toFixed(4),
    (lat + radiusKm * 1.5 / 111).toFixed(4),
    (lng + radiusKm * 1.5 / 111).toFixed(4),
    (lat - radiusKm * 1.5 / 111).toFixed(4),
  ].join(",");

  const urls = queries.map(
    (q) =>
      `https://nominatim.openstreetmap.org/search?q=${q}&format=json&limit=50&viewbox=${viewbox}&addressdetails=1&extratags=1`
  );

  const allResults: any[] = [];
  // Run queries in parallel
  const settled = await Promise.allSettled(urls.map((url) => fetchNominatim(url)));
  for (const s of settled) {
    if (s.status === "fulfilled") allResults.push(...s.value);
  }

  return allResults;
}

async function fetchFromOverpass(lat: number, lng: number, radiusM: number): Promise<any[]> {
  const query = `
[out:json][timeout:10];
(
  node["amenity"="pharmacy"](around:${radiusM},${lat},${lng});
  node["amenity"="hospital"](around:${radiusM},${lat},${lng});
  node["amenity"="clinic"](around:${radiusM},${lat},${lng});
  node["amenity"="doctors"](around:${radiusM},${lat},${lng});
  way["amenity"="pharmacy"](around:${radiusM},${lat},${lng});
  way["amenity"="hospital"](around:${radiusM},${lat},${lng});
  way["amenity"="clinic"](around:${radiusM},${lat},${lng});
  node["shop"="chemist"](around:${radiusM},${lat},${lng});
);
out center body;`;

  try {
    const response = await undiciFetch("https://overpass-api.de/api/interpreter", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `data=${encodeURIComponent(query)}`,
    });

    if (!response.ok) {
      process.stderr.write(`[pharmacy] Overpass HTTP ${response.status}\n`);
      return [];
    }

    const data: any = await response.json();
    const elements: any[] = data.elements || [];

    return elements.map((el) => {
      const tags = el.tags || {};
      const elLat = el.lat || el.center?.lat;
      const elLng = el.lon || el.center?.lon;
      const amenity = tags.amenity || "";
      const shop = tags.shop || "";

      return {
        osm_id: el.id,
        name: tags.name || tags["name:en"] || "Unknown",
        class: amenity || shop,
        type: amenity === "pharmacy" || shop === "chemist" ? "pharmacy" : amenity,
        lat: String(elLat),
        lon: String(elLng),
        display_name: [tags.name, tags["addr:street"], tags["addr:housenumber"], tags["addr:city"]]
          .filter(Boolean)
          .join(", ") || "Address not available",
        extratags: {
          phone: tags.phone || tags["contact:phone"] || "",
          opening_hours: tags.opening_hours || "",
        },
      };
    });
  } catch (err: any) {
    process.stderr.write(`[pharmacy] Overpass failed: ${err.message}\n`);
    return [];
  }
}

router.get("/nearby", async (req: Request, res: Response) => {
  const lat = parseFloat(req.query.lat as string);
  const lng = parseFloat(req.query.lng as string);
  const radiusKm = parseFloat((req.query.radius as string) || "10");

  if (isNaN(lat) || isNaN(lng)) {
    return res.status(400).json({ error: "lat and lng query params are required" });
  }

  try {
    const raw = await fetchPharmacies(lat, lng, radiusKm);
    const results = parseResults(raw, lat, lng, radiusKm);
    process.stderr.write(`[pharmacy] returning ${results.length} results\n`);
    res.json(results);
  } catch (err: any) {
    process.stderr.write(`[pharmacy] error: ${err.message}\n`);
    res.status(502).json({ error: "Failed to fetch pharmacy data", detail: err.message });
  }
});

export default router;
