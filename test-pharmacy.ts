import https from "https";

function httpsGet(url: string): Promise<any> {
  return new Promise((resolve, reject) => {
    https
      .get(url, { headers: { "User-Agent": "MediGuideApp/1.0" } }, (res) => {
        let data = "";
        res.on("data", (chunk: string) => (data += chunk));
        res.on("end", () => {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(new Error("Invalid JSON from Nominatim"));
          }
        });
      })
      .on("error", reject);
  });
}

const lat = 14.5995;
const lng = 120.9842;
const radiusKm = 5;

const viewbox = [
  (lng - radiusKm / 111).toFixed(4),
  (lat + radiusKm / 111).toFixed(4),
  (lng + radiusKm / 111).toFixed(4),
  (lat - radiusKm / 111).toFixed(4),
].join(",");

const url = `https://nominatim.openstreetmap.org/search?q=pharmacy&format=json&limit=20&viewbox=${viewbox}&bounded=1`;
console.log("URL:", url);

httpsGet(url)
  .then((data) => {
    console.log("Results:", data.length);
    data.slice(0, 3).forEach((r: any) => console.log(" -", r.name, r.type));
  })
  .catch((err) => {
    console.error("Error:", err.message);
  });
