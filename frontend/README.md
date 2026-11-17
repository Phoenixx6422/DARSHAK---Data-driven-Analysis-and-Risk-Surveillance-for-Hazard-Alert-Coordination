# Aegis · Pre-Disaster Management & Early Warning System

A static, desktop-first frontend prototype for a pre-disaster monitoring dashboard. It uses plain HTML, CSS, and vanilla JavaScript; there is no build step or package install.

## Run locally

- Open `index.html` directly in a modern browser, or
- Open the project folder in VS Code and use Live Server.

The Leaflet maps and remote icons/tiles require an internet connection. The project includes local mock JSON files. When opened with `file://`, the frontend uses a small in-code fallback because browsers commonly block `fetch()` requests to local files. When served from Live Server, it reads the JSON files in `data/mock/`.

## Pages and features

- **Home:** current alert status, local safety score and weather, South Asia mini map, and recent news.
- **Map:** interactive risk zones with clickable SafetyScore popups, cyclone track, selectable hazard layers, and layer-specific data.
- **News:** disaster updates with a type filter.
- **Profile:** demo profile and emergency contacts, inline editing, client-side validation, and alert preferences.

The authority-facing workflow is monitor-only. Alerts are displayed automatically; the prototype has no approval or classification controls. Low and moderate conditions provide risk information and advisory context, while high/critical alerts are highlighted. Estimates are model-based and uncertain; follow official guidance.

All visible sample content is simulated. The mock profile save is held in memory only and is cleared on reload. Do not enter real personal information: real storage must be handled securely by a backend over HTTPS.

## Folder structure

```text
index.html
map.html
news.html
profile.html
css/
  styles.css
js/
  api.js        data access layer (mock now, real backend later)
  utils.js      pure helper functions (unit tested)
  layout.js     shared header and sidebar
  home.js
  map.js
  news.js
  profile.js
data/
  mock/
    alerts.json
    live-data.json
    news.json
    profile.json
    risk-zones.json
    weather.json
tests/
  utils.test.js            unit tests for js/utils.js
  api.test.js              unit tests for js/api.js (mock mode)
  api-file-protocol.test.js  unit test for the file:// fallback
package.json
```

## Unit tests

The tests use Jest. You need Node.js (LTS) installed.

```bash
npm install       # first time only
npm test          # runs every test and lists PASS/FAIL for each one
npm run coverage  # writes coverage/lcov-report/index.html (open it in a browser)
```

What is covered:

- `js/utils.js`: every function, with equivalence-partition and boundary-value cases (for example phone length 6, 7, 15 and 16 digits).
- `js/api.js`: every mock method and each of its branches (alert active or not, zone found or not, unknown layer, network and HTTP errors, `file://` fallback).

What is not covered by Jest: the page scripts (`home.js`, `map.js`, `news.js`, `profile.js`, `layout.js`). They mainly change the page, so they are checked by the manual checklist below.

Manual checklist (run in the browser after `npm test`):

1. Home: the alert banner, SafetyScore bar, weather values and news list all appear.
2. Map: switch between Risk Zones, Cyclone, Rainfall, Flood, Wind and Pressure; the live-data panel updates.
3. News: change the type filter; the count text updates.
4. Profile: enter an invalid phone number and see the error; save a valid one and see the confirmation.

## Connect a real API

`js/api.js` is the data access boundary. It exposes `getActiveAlert()`, `getSafetyScore(lat, lng)`, `getWeather(lat, lng)`, `getNews()`, `getRiskZones(type)`, `getLiveData(type)`, `getProfile()`, and `saveProfile(data)`.

1. Configure your backend base URL before `js/api.js` loads, for example with a small script in each page: `window.AEGIS_API_BASE_URL = "https://your-backend.example/api";`.
2. Change `const USE_MOCK = true;` to `false` in `js/api.js`.
3. Implement the REST routes used in that file and return the same data shapes as the mock JSON. Profile saving uses `PUT /profile`; the other route paths are defined alongside each API method.
4. Serve the frontend and backend over HTTPS in production. Keep secrets and personal-data persistence on the backend; do not put credentials in the frontend.

The example URL above is a placeholder, not a live service. No API keys are required for this prototype.
