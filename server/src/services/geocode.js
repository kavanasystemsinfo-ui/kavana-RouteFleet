// Geocodificación de direcciones a coordenadas (lat/lng).
// Usa Nominatim (OpenStreetMap) — gratuito, sin API key.
// Se cachea en memoria para no repetir peticiones iguales en el mismo arranque.

const NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search';

// Caché simple en memoria: address -> {lat, lng}
const cache = new Map();

// Geocodifica una dirección de texto a {lat, lng}.
// Devuelve null si no se encuentra.
export async function geocodeAddress(address) {
  if (!address) return null;
  const key = address.trim().toLowerCase();
  if (cache.has(key)) return cache.get(key);

  try {
    const url = `${NOMINATIM_URL}?format=json&limit=1&q=${encodeURIComponent(address)}`;
    const res = await fetch(url, {
      headers: { 'User-Agent': 'KAVANA-RouteFleet/1.0 (routefleet@kavanasystems.com)' }
    });
    if (!res.ok) return null;
    const data = await res.json();
    if (!Array.isArray(data) || data.length === 0) {
      cache.set(key, null);
      return null;
    }
    const result = { lat: parseFloat(data[0].lat), lng: parseFloat(data[0].lon) };
    cache.set(key, result);
    return result;
  } catch (err) {
    console.error('Geocode error:', err.message);
    return null;
  }
}
