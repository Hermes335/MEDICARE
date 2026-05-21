import { Router, Request, Response } from "express";

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

router.get("/nearby", async (req: Request, res: Response) => {
  const lat = parseFloat(req.query.lat as string);
  const lng = parseFloat(req.query.lng as string);
  const radiusKm = parseFloat((req.query.radius as string) || "5");

  if (isNaN(lat) || isNaN(lng)) {
    return res.status(400).json({ error: "lat and lng query params are required" });
  }

  try {
    const viewbox = [
      (lng - radiusKm / 111).toFixed(4),
      (lat + radiusKm / 111).toFixed(4),
      (lng + radiusKm / 111).toFixed(4),
      (lat - radiusKm / 111).toFixed(4),
    ].join(",");

    const nominatimUrl =
      "https://nominatim.openstreetmap.org/search?q=pharmacy&format=json&limit=20&viewbox=" +
      viewbox +
      "&bounded=1";

    console.log("[pharmacy] fetching", nominatimUrl);

    const response = await fetch(nominatimUrl, {
      headers: { "User-Agent": "MediGuideApp/1.0" },
    });

    console.log("[pharmacy] response status", response.status);

    if (!response.ok) {
      console.log("[pharmacy] non-ok response:", response.status, response.statusText);
      return res.json([]);
    }

    const pharmacies: any[] = await response.json();
    console.log("[pharmacy] got", pharmacies.length, "results");

    const seen = new Set<string>();
    const results = pharmacies
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
        const isPharmacy = el.type === "pharmacy" || el.class === "pharmacy";
        return {
          id: String(el.osm_id),
          name: el.name || "Unknown",
          type: isPharmacy ? "pharmacy" : "clinic",
          distance: formatDistance(dist),
          distanceKm: dist,
          address: el.display_name || "Address not available",
          lat: elLat,
          lng: elLng,
          phone: "",
          isOpen: true,
        };
      })
      .filter((p: any) => p.distanceKm <= radiusKm)
      .sort((a: any, b: any) => a.distanceKm - b.distanceKm)
      .slice(0, 20);

    res.json(results);
  } catch (err: any) {
    console.error("[pharmacy] CATCH:", err.message, err.stack);
    res.status(502).json({ error: "Failed to fetch pharmacy data", detail: err.message });
  }
});

export default router;
