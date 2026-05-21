const { fetch } = require('undici');

async function main() {
  const [, , lat, lng, radius = '5'] = process.argv;
  if (!lat || !lng) {
    console.error('lat and lng required');
    process.exit(2);
  }

  const radiusKm = parseFloat(radius);
  const viewbox = [
    (parseFloat(lng) - radiusKm / 111).toFixed(4),
    (parseFloat(lat) + radiusKm / 111).toFixed(4),
    (parseFloat(lng) + radiusKm / 111).toFixed(4),
    (parseFloat(lat) - radiusKm / 111).toFixed(4),
  ].join(',');

  const nominatimUrl =
    'https://nominatim.openstreetmap.org/search?q=pharmacy&format=json&limit=20&viewbox=' +
    viewbox +
    '&bounded=1';

  try {
    const res = await fetch(nominatimUrl, { headers: { 'User-Agent': 'MediGuideApp/1.0' } });
    if (!res.ok) {
      const t = await res.text();
      console.error('non-ok', res.status, res.statusText, t);
      process.exit(3);
    }
    const data = await res.json();
    console.log(JSON.stringify(data));
    process.exit(0);
  } catch (err) {
    console.error('error', err && err.message ? err.message : err);
    process.exit(4);
  }
}

main();
