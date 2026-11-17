(() => {
  const layerDefinitions = [
    { name: "Risk Zones", icon: "shield-alert" },
    { name: "Cyclone", icon: "tornado" },
    { name: "Rainfall", icon: "cloud-rain" },
    { name: "Flood", icon: "waves" },
    { name: "Wind", icon: "wind" },
    { name: "Pressure", icon: "gauge" }
  ];
  const severityColors = { Low: "#42b77b", Moderate: "#e7c63f", High: "#f18a35", Critical: "#df4b4d" };
  let map;
  let activeOverlay;
  let cycloneMarker;
  let currentLayer = "Risk Zones";
  let zones = [];

  function showMapError(message) {
    const error = document.getElementById("map-error");
    error.textContent = message;
    error.hidden = false;
  }

  function createHeatLayer(weights) {
    if (!L.heatLayer) return null;
    return L.heatLayer(weights, {
      radius: 40, blur: 30, maxZoom: 8, minOpacity: .32,
      gradient: { 0.2: "#44b779", 0.45: "#e8c841", 0.68: "#f18b37", 1: "#df4849" }
    });
  }

  function addZonePopups(group) {
    zones.forEach(zone => {
      const color = severityColors[zone.level] || severityColors.Moderate;
      L.circleMarker([zone.lat, zone.lng], {
        radius: zone.level === "Critical" ? 9 : 7,
        color: "#fff", weight: 2, fillColor: color, fillOpacity: .93
      }).bindPopup(`<div class="zone-popup"><strong>${escapeHtml(zone.name)}</strong><span>SafetyScore: ${escapeHtml(zone.score)} / 100</span><br><span>Risk level: ${escapeHtml(zone.level)}</span></div>`).addTo(group);
    });
  }

  function addCyclone(group) {
    const track = [[12.2, 87.6], [13.1, 87.8], [14.1, 88.0], [15.2, 88.4], [16.4, 88.8], [17.6, 89.1]];
    L.polyline(track, { color: "#df4851", weight: 3, opacity: .8, dashArray: "7 7" }).addTo(group);
    if (!cycloneMarker) {
      cycloneMarker = L.marker([15.2, 88.4], {
        icon: L.divIcon({ className: "cyclone-div-icon", html: '<div class="cyclone-marker"><i data-lucide="tornado"></i></div>' })
      }).bindPopup("<strong>Cyclone alert</strong><br>120 km/h · Bay of Bengal");
    }
    cycloneMarker.addTo(group);
  }

  function addFloodRegion(group) {
    const affected = [
      [[21.7, 88.1], [22.9, 88.1], [23.1, 90.5], [21.5, 91.3], [20.9, 89.5]],
      [[25.1, 90.1], [26.2, 90.4], [26.7, 92.1], [25.6, 92.6], [24.9, 91.5]]
    ];
    affected.forEach(coords => L.polygon(coords, {
      color: "#2777da", fillColor: "#4b9ce7", weight: 2, fillOpacity: .38
    }).addTo(group).bindPopup("<strong>Flood watch area</strong><br>Monitor local advisories."));
  }

  function buildLayer(name) {
    const group = L.layerGroup();
    const weights = zones.map(zone => {
      const weight = name === "Rainfall" ? Math.min(1, zone.weight * 1.15) : zone.weight;
      return [zone.lat, zone.lng, weight];
    });

    if (name === "Flood") {
      addFloodRegion(group);
    } else if (name === "Cyclone") {
      const heat = createHeatLayer(weights);
      if (heat) heat.addTo(group);
      addCyclone(group);
    } else {
      const heat = createHeatLayer(weights);
      if (heat) heat.addTo(group);
      if (name === "Wind" || name === "Pressure") {
        L.circle([15.2, 88.4], {
          radius: 115000, color: "#3486dc", fillColor: "#559bed", fillOpacity: .16, weight: 2
        }).addTo(group).bindPopup("<strong>Wind observation</strong><br>120 km/h · NE");
        L.circle([15.2, 88.4], {
          radius: 175000, color: "#8057c6", fillColor: "#9c74da", fillOpacity: .08, weight: 2
        }).addTo(group).bindPopup("<strong>Pressure observation</strong><br>980 hPa · Falling");
      }
    }
    if (name === "Risk Zones" || name === "Rainfall") addZonePopups(group);
    if (name === "Risk Zones") addCyclone(group);
    return group;
  }

  function updateActiveLayer(name) {
    currentLayer = name;
    document.querySelectorAll(".layer-nav-item").forEach(button => {
      const active = button.dataset.layer === name;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    document.querySelectorAll(".layers-menu button").forEach(button => button.classList.toggle("is-active", button.dataset.layer === name));
    document.getElementById("map-layer-label").innerHTML = `<i data-lucide="${layerDefinitions.find(layer => layer.name === name).icon}"></i><span>${escapeHtml(name)}</span>`;
    document.getElementById("live-layer-name").textContent = name;
    if (window.lucide) window.lucide.createIcons();
    if (activeOverlay) map.removeLayer(activeOverlay);
    activeOverlay = buildLayer(name).addTo(map);
    updateLiveData(name);
  }

  function renderLiveData(data) {
    const container = document.getElementById("live-data-content");
    if (!data || !Object.keys(data).length) {
      document.getElementById("live-updated").textContent = "—";
      container.innerHTML = '<p class="no-data">No data available for this layer.</p>';
      return;
    }
    document.getElementById("live-updated").textContent = data.lastUpdated || "—";
    const icons = {
      windSpeed: "wind", pressure: "gauge", location: "map-pin", rainfall: "cloud-rain",
      intensity: "cloud-drizzle", affectedArea: "waves", alertLevel: "triangle-alert",
      gusts: "wind", direction: "compass", trend: "activity"
    };
    const labels = {
      windSpeed: "Wind Speed", pressure: "Pressure", location: "Location", rainfall: "Rainfall",
      intensity: "Intensity", affectedArea: "Affected Area", alertLevel: "Alert Level",
      gusts: "Wind Gusts", direction: "Direction", trend: "Pressure Trend"
    };
    container.innerHTML = Object.entries(data).filter(([key]) => key !== "lastUpdated").map(([key, value]) => `
      <div class="live-metric"><i><i data-lucide="${icons[key] || "activity"}"></i></i>
        <div><span>${escapeHtml(labels[key] || key)}</span><strong>${escapeHtml(value)}</strong></div>
      </div>`).join("");
    if (window.lucide) window.lucide.createIcons();
  }

  async function updateLiveData(name) {
    const container = document.getElementById("live-data-content");
    container.innerHTML = '<p class="no-data">Loading layer data…</p>';
    try {
      const data = await getLiveData(name);
      renderLiveData(data);
    } catch (error) {
      container.innerHTML = `<p class="no-data">${escapeHtml(error.message)}</p>`;
    }
  }

  function populateLayerMenu() {
    const menu = document.getElementById("layers-menu");
    menu.innerHTML = layerDefinitions.map(layer => `<button type="button" data-layer="${escapeHtml(layer.name)}" class="${layer.name === currentLayer ? "is-active" : ""}"><i data-lucide="${layer.icon}"></i>${escapeHtml(layer.name)}</button>`).join("");
    menu.addEventListener("click", event => {
      const button = event.target.closest("button[data-layer]");
      if (button) {
        updateActiveLayer(button.dataset.layer);
        menu.hidden = true;
      }
    });
    document.getElementById("layers-toggle").addEventListener("click", () => { menu.hidden = !menu.hidden; });
    document.addEventListener("click", event => {
      if (!event.target.closest(".layers-menu-wrap")) menu.hidden = true;
    });
    document.querySelectorAll(".layer-nav-item").forEach(button => button.addEventListener("click", () => updateActiveLayer(button.dataset.layer)));
    if (window.lucide) window.lucide.createIcons();
  }

  function searchLocation(query) {
    const position = findKnownPlace(query);
    if (position) map.setView(position, 7);
    else showMapError(`No map match for “${query}”. Try a city or country in South Asia.`);
  }

  async function initializeMap() {
    if (!window.L) {
      showMapError("The map service could not load. Check your internet connection and try again.");
      return;
    }
    map = L.map("risk-map", { zoomControl: false, preferCanvas: true }).setView([21.8, 84.5], 5);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
    L.control.zoom({ position: "topright" }).addTo(map);
    populateLayerMenu();
    try {
      const result = await getRiskZones("Risk Zones");
      zones = result.zones || [];
      updateActiveLayer("Risk Zones");
    } catch (error) {
      showMapError(error.message);
    }
    window.addEventListener("aegis:search", event => searchLocation(event.detail.query));
    const requestedLocation = new URLSearchParams(window.location.search).get("location");
    if (requestedLocation) {
      const search = document.getElementById("location-search");
      search.value = requestedLocation;
      searchLocation(requestedLocation);
    }
    window.setTimeout(() => map.invalidateSize(), 100);
    if (window.lucide) window.lucide.createIcons();
  }

  initializeMap();
})();
