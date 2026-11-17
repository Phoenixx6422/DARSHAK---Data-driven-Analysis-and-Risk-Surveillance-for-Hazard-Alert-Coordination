/**
 * @jest-environment jsdom
 */

/*
 * Unit tests for js/api.js in mock mode (USE_MOCK = true), served over http
 * the way VS Code Live Server does it: each call reads data/mock/*.json via fetch.
 *
 * Techniques: black-box (given this mock state, expect this result) and
 * white-box (one test per branch: found / not found, active / inactive,
 * fetch ok / fetch failed / HTTP error, unknown layer type).
 */

const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");

// Jest's jsdom environment does not provide structuredClone (every modern browser does).
// This polyfill only exists so the tests run; the app code itself is unchanged.
if (typeof structuredClone === "undefined") {
  global.structuredClone = value => JSON.parse(JSON.stringify(value));
}

function readMock(file) {
  return JSON.parse(fs.readFileSync(path.join(ROOT, "data", "mock", file), "utf8"));
}

function fakeResponse(body, ok = true, status = 200) {
  return { ok, status, json: async () => body };
}

// Serves data/mock/*.json from disk, optionally overriding individual files.
function diskFetch(overrides = {}) {
  return async url => {
    const file = String(url).replace("data/mock/", "");
    if (Object.prototype.hasOwnProperty.call(overrides, file)) return fakeResponse(overrides[file]);
    return fakeResponse(readMock(file));
  };
}

// Loads a fresh copy of api.js (fresh cache) with the given fetch behaviour.
function loadApi(fetchImpl) {
  jest.resetModules();
  global.fetch = jest.fn(fetchImpl);
  return require("../js/api");
}

beforeEach(() => {
  localStorage.clear();
});

describe("getActiveAlert (branch: active vs inactive)", () => {
  test("returns the alert when active is true", async () => {
    const api = loadApi(diskFetch());
    const alert = await api.getActiveAlert();
    expect(alert).toMatchObject({ title: "Cyclone Alert", level: "High" });
  });

  test("returns null when no alert is active", async () => {
    const api = loadApi(diskFetch({ "alerts.json": { active: false } }));
    expect(await api.getActiveAlert()).toBeNull();
  });
});

describe("getSafetyScore (branch: matching zone found / not found)", () => {
  test("exact coordinates return the Lucknow zone", async () => {
    const api = loadApi(diskFetch());
    const zone = await api.getSafetyScore(26.8467, 80.9462);
    expect(zone).toMatchObject({ name: "Lucknow Region", score: 72, level: "Moderate" });
  });

  test("a nearby point within tolerance returns the same zone", async () => {
    const api = loadApi(diskFetch());
    const zone = await api.getSafetyScore(26.9, 81.0);
    expect(zone.name).toBe("Lucknow Region");
  });

  test("a location far from every zone returns null (no fallback zone)", async () => {
    const api = loadApi(diskFetch());
    expect(await api.getSafetyScore(0, 0)).toBeNull();
  });
});

describe("getWeather, getNews, getRiskZones (data shape)", () => {
  test("getWeather returns the weather fields used by the home page", async () => {
    const api = loadApi(diskFetch());
    const weather = await api.getWeather(26.8, 80.9);
    expect(weather.temperature).toBe(26);
    expect(weather.windSpeed).toBe("120 km/h");
  });

  test("getNews returns the list of news items", async () => {
    const api = loadApi(diskFetch());
    const items = await api.getNews();
    expect(Array.isArray(items)).toBe(true);
    expect(items).toHaveLength(5);
    expect(items[0].type).toBe("Cyclone");
  });

  test("getRiskZones returns the zones and echoes the requested type", async () => {
    const api = loadApi(diskFetch());
    const result = await api.getRiskZones("Risk Zones");
    expect(result.type).toBe("Risk Zones");
    expect(result.zones).toHaveLength(8);
  });
});

describe("getLiveData (branch: known layer vs unknown layer)", () => {
  test("a known layer returns its live metrics", async () => {
    const api = loadApi(diskFetch());
    const data = await api.getLiveData("Cyclone");
    expect(data.windSpeed).toBe("120 km/h");
  });

  test("an unknown layer returns null so the page shows 'No data available'", async () => {
    const api = loadApi(diskFetch());
    expect(await api.getLiveData("Tsunami")).toBeNull();
  });
});

describe("getProfile and saveProfile (demo storage rules)", () => {
  test("getProfile returns a copy: changing it does not change the next read", async () => {
    const api = loadApi(diskFetch());
    const first = await api.getProfile();
    first.name = "Changed locally";
    const second = await api.getProfile();
    expect(second.name).toBe("User Name");
  });

  test("a saved profile is returned by the next getProfile call", async () => {
    const api = loadApi(diskFetch());
    const profile = await api.getProfile();
    await api.saveProfile({ ...profile, name: "Test User" });
    expect((await api.getProfile()).name).toBe("Test User");
  });

  test("saving never writes to localStorage (privacy rule: demo data stays in memory)", async () => {
    const api = loadApi(diskFetch());
    await api.saveProfile({ ...(await api.getProfile()), name: "Private" });
    expect(localStorage.length).toBe(0);
  });
});

describe("error handling when data cannot be loaded (branch: fetch failed / HTTP error)", () => {
  test("a network failure gives a friendly message", async () => {
    const api = loadApi(() => Promise.reject(new TypeError("Failed to fetch")));
    await expect(api.getWeather(0, 0)).rejects.toThrow("We couldn't load the demo data");
  });

  test("an HTTP error response gives the same friendly message", async () => {
    const api = loadApi(async () => fakeResponse({}, false, 404));
    await expect(api.getNews()).rejects.toThrow("We couldn't load the demo data");
  });
});
