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

    process.stderr.write(`[pharmacy] fetching ${nominatimUrl}\n`);

    const response = await undiciFetch(nominatimUrl, {
      headers: { "User-Agent": "MediGuideApp/1.0" },
    });

    process.stderr.write(`[pharmacy] response status ${response.status}\n`);

    if (!response.ok) {
      let bodyText = "";
      try {
        bodyText = await response.text();
      } catch (e: any) {
        bodyText = `<failed to read response text: ${e?.message || e}>`;
      }
      process.stderr.write(`[pharmacy] non-ok response: ${response.status} ${response.statusText} body: ${bodyText}\n`);
      return res.status(502).json({ error: "Failed to fetch pharmacy data", detail: bodyText });
    }

    const pharmacies: any[] = await response.json();
    process.stderr.write(`[pharmacy] got ${pharmacies.length} results\n`);

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
    process.stderr.write(`[pharmacy] CATCH (fetch): ${err?.message || err}\n`);
    // Fallback: spawn a plain `node` process to run a standalone script that performs the same fetch.
    try {
      const scriptPath = path.join(process.cwd(), "server", "standalone-pharmacy.cjs");
      process.stderr.write(`[pharmacy] attempting child_process fallback using: ${scriptPath}\n`);

      const child = spawn(process.execPath, [scriptPath, String(lat), String(lng), String(radiusKm)], {
        cwd: process.cwd(),
        env: process.env,
        stdio: ["ignore", "pipe", "pipe"],
      });

      let stdout = "";
      let stderr = "";
      const timeout = setTimeout(() => {
        try {
          child.kill();
        } catch (e) {
          /* ignore */
        }
      }, 10_000);

      child.stdout.on("data", (chunk) => (stdout += chunk.toString()));
      child.stderr.on("data", (chunk) => (stderr += chunk.toString()));

      child.on("close", (code) => {
        clearTimeout(timeout);
        if (code === 0 && stdout) {
          try {
            const pharmacies = JSON.parse(stdout);
            process.stderr.write(`[pharmacy] child fallback got ${pharmacies.length} results\n`);
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

            return res.json(results);
          } catch (parseErr) {
            process.stderr.write(`[pharmacy] child stdout parse error: ${parseErr} stdout: ${stdout} stderr: ${stderr}\n`);
            return res.status(502).json({ error: "Failed to fetch pharmacy data", detail: stderr || parseErr.message });
          }
        }

        process.stderr.write(`[pharmacy] child process failed code: ${code} stderr: ${stderr}\n`);
        return res.status(502).json({ error: "Failed to fetch pharmacy data", detail: stderr || "child process failed" });
      });
    } catch (childErr: any) {
      process.stderr.write(`[pharmacy] fallback failed: ${childErr?.message || childErr}\n`);
      res.status(502).json({ error: "Failed to fetch pharmacy data", detail: childErr?.message || String(childErr) });
    }
  }
});

export default router;
