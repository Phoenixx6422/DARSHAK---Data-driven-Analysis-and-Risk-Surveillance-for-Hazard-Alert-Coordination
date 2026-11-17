// Set USE_MOCK to false and define window.AEGIS_API_BASE_URL before this file to use a backend.
const USE_MOCK = true;
const BASE_URL = window.AEGIS_API_BASE_URL || "";

const mockFallback = {
  "alerts.json": {
    active: true,
    title: "Cyclone Alert",
    description: "High risk of heavy rainfall in Eastern Coast in next 48 hours",
    location: "Eastern Coast",
    level: "High",
    updated: "3 hours ago"
  },
  "weather.json": {
    temperature: 26,
    condition: "Heavy Rain",
    horizon: "Next 24h",
    rainfall: "84 mm",
    windSpeed: "120 km/h",
    pressure: "980 hPa"
  },
  "risk-zones.json": {
    zones: [
      { name: "Bay of Bengal", lat: 18.4, lng: 88.2, score: 24, level: "Critical", weight: 1.0 },
      { name: "Odisha Coast", lat: 20.2, lng: 86.8, score: 38, level: "High", weight: 0.82 },
      { name: "Eastern India", lat: 23.1, lng: 84.4, score: 52, level: "Moderate", weight: 0.62 },
      { name: "Bangladesh Coast", lat: 22.4, lng: 90.2, score: 34, level: "High", weight: 0.78 },
      { name: "Central India", lat: 21.2, lng: 78.1, score: 65, level: "Moderate", weight: 0.38 },
      { name: "Lucknow Region", lat: 26.8467, lng: 80.9462, score: 72, level: "Moderate", weight: 0.32 },
      { name: "Western Bay", lat: 16.8, lng: 84.4, score: 42, level: "High", weight: 0.7 },
      { name: "Assam", lat: 26.4, lng: 92.4, score: 57, level: "Moderate", weight: 0.54 }
    ]
  },
  "news.json": {
    items: [
      { id: 1, type: "Cyclone", headline: "Cyclone alert issued for the Eastern Coast", source: "Regional Weather Desk", time: "2 hours ago", image: "https://images.unsplash.com/photo-1527482797697-8795b05a13fe?auto=format&fit=crop&w=360&q=80", summary: "Strong winds and heavy rain are possible along coastal districts over the next 48 hours." },
      { id: 2, type: "Rainfall", headline: "Heavy rainfall in Assam, rivers above danger level", source: "Weather Monitor", time: "5 hours ago", image: "https://images.unsplash.com/photo-1519692933481-e162a57d6721?auto=format&fit=crop&w=360&q=80", summary: "Residents near river banks are advised to monitor local updates and avoid flooded roads." },
      { id: 3, type: "Landslide", headline: "Landslide risk increased in Uttarakhand", source: "Regional Weather Desk", time: "1 day ago", image: "https://images.unsplash.com/photo-1511497584788-876760111969?auto=format&fit=crop&w=360&q=80", summary: "Recent rainfall has increased the possibility of slope instability in vulnerable areas." },
      { id: 4, type: "Flood", headline: "Flood watch continues for low-lying delta districts", source: "Community Resilience Bulletin", time: "1 day ago", image: "https://images.unsplash.com/photo-1547683905-f686c993aae5?auto=format&fit=crop&w=360&q=80", summary: "Keep emergency supplies accessible and follow instructions from local officials." },
      { id: 5, type: "Rainfall", headline: "Monsoon showers expected across central India", source: "Weather Monitor", time: "2 days ago", image: "https://images.unsplash.com/photo-1433863448220-78aaa064ff47?auto=format&fit=crop&w=360&q=80", summary: "Scattered showers are forecast, with locally heavy rain possible in some districts." }
    ]
  },
  "profile.json": {
    name: "User Name",
    email: "user@example.com",
    phone: "+91 98765 43210",
    location: "Lucknow, Uttar Pradesh",
    lat: 26.8467,
    lng: 80.9462,
    familyContacts: [
      { name: "Ananya Sharma", phone: "+91 98765 43211" },
      { name: "Rohan Sharma", phone: "+91 98765 43212" }
    ],
    emergencyContact: "Emergency contact: +91 112",
    bloodGroup: "B+",
    otherInfo: "Asthma medication in emergency kit",
    preferences: { smsAlerts: true, emailAlerts: true, appAlerts: true }
  },
  "live-data.json": {
    "Risk Zones": { windSpeed: "120 km/h", pressure: "980 hPa", location: "15.2°N, 88.4°E", lastUpdated: "3 hours ago" },
    "Cyclone": { windSpeed: "120 km/h", pressure: "980 hPa", location: "15.2°N, 88.4°E", lastUpdated: "3 hours ago" },
    "Rainfall": { rainfall: "84 mm / 24h", intensity: "Heavy", location: "Eastern Coast", lastUpdated: "1 hour ago" },
    "Flood": { affectedArea: "Low-lying delta districts", alertLevel: "Watch", location: "Bangladesh Coast", lastUpdated: "2 hours ago" },
    "Wind": { windSpeed: "120 km/h", gusts: "145 km/h", direction: "NE", location: "15.2°N, 88.4°E", lastUpdated: "3 hours ago" },
    "Pressure": { pressure: "980 hPa", trend: "Falling", location: "Bay of Bengal", lastUpdated: "3 hours ago" }
  }
};

let profileDraft = null;
const mockCache = {};

async function requestApi(path, options) {
  if (!BASE_URL) throw new Error("Connect a backend by setting AEGIS_API_BASE_URL before disabling mock data.");
  let response;
  try {
    response = await fetch(`${BASE_URL.replace(/\/$/, "")}${path}`, {
      ...options,
      headers: { "Content-Type": "application/json", ...(options && options.headers) }
    });
  } catch (error) {
    throw new Error("We couldn't connect to the service. Please check your connection and try again.");
  }
  if (!response.ok) throw new Error(`The service returned an error (${response.status}). Please try again later.`);
  return response.status === 204 ? null : response.json();
}

async function getMockFile(filename) {
  if (mockCache[filename]) return mockCache[filename];
  if (window.location.protocol === "file:") {
    mockCache[filename] = mockFallback[filename];
    return mockCache[filename];
  }
  try {
    const response = await fetch(`data/mock/${filename}`);
    if (!response.ok) throw new Error(`Could not load ${filename} (${response.status}).`);
    mockCache[filename] = await response.json();
    return mockCache[filename];
  } catch (error) {
    throw new Error("We couldn't load the demo data. Please check that the project files are available and try again.");
  }
}

async function apiGet(path, filename, select) {
  const result = USE_MOCK ? await getMockFile(filename) : await requestApi(path);
  return select ? select(result) : result;
}

async function getActiveAlert() {
  return apiGet("/alerts/active", "alerts.json", data => data.active ? data : null);
}

async function getSafetyScore(lat, lng) {
  if (!USE_MOCK) return requestApi(`/risk/score?lat=${encodeURIComponent(lat)}&lng=${encodeURIComponent(lng)}`);
  const zones = await getRiskZones("Risk Zones");
  return zones.zones.find(zone => Math.abs(zone.lat - lat) < 3 && Math.abs(zone.lng - lng) < 4) || null;
}

async function getWeather(lat, lng) {
  return apiGet(`/weather?lat=${encodeURIComponent(lat)}&lng=${encodeURIComponent(lng)}`, "weather.json");
}

async function getNews() {
  return apiGet("/news", "news.json", data => data.items);
}

async function getRiskZones(type) {
  if (!USE_MOCK) return requestApi(`/risk/zones?type=${encodeURIComponent(type)}`);
  const data = await getMockFile("risk-zones.json");
  return { ...data, type };
}

async function getLiveData(type) {
  if (!USE_MOCK) return requestApi(`/map/live-data?layer=${encodeURIComponent(type)}`);
  const data = await getMockFile("live-data.json");
  return data[type] || null;
}

async function getProfile() {
  if (!USE_MOCK) return requestApi("/profile");
  if (profileDraft) return structuredClone(profileDraft);
  return structuredClone(await getMockFile("profile.json"));
}

async function saveProfile(data) {
  if (!USE_MOCK) return requestApi("/profile", { method: "PUT", body: JSON.stringify(data) });
  // Demo-only in-memory storage; real storage will be handled securely by the backend over HTTPS.
  profileDraft = structuredClone(data);
  return structuredClone(profileDraft);
}

if (typeof module !== "undefined") {
  module.exports = {
    getActiveAlert, getSafetyScore, getWeather, getNews, getRiskZones,
    getLiveData, getProfile, saveProfile
  };
}
