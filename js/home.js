function showToast(message, isError) {
  const toast = document.getElementById("toast");
  if (!toast) return;
  toast.textContent = message;
  toast.classList.toggle("is-error", Boolean(isError));
  toast.classList.add("is-visible");
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => toast.classList.remove("is-visible"), 3200);
}

function renderNewsItem(item, compact) {
  const image = escapeHtml(item.image);
  const headline = escapeHtml(item.headline);
  return `<article class="news-item">
    <img class="news-thumb" src="${image}" alt="" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=360&q=70'">
    <div class="news-item-content"><h3>${headline}</h3>
      ${compact ? "" : `<p class="news-summary">${escapeHtml(item.summary || "")}</p>`}
      <div class="news-meta"><span class="news-type">${escapeHtml(item.type)}</span><span class="meta-dot"></span><span class="news-source">${escapeHtml(item.source)}</span><span class="meta-dot"></span><span>${escapeHtml(item.time)}</span></div>
    </div>
  </article>`;
}

async function initializeHome() {
  const content = document.querySelector(".home-content");
  content.setAttribute("aria-busy", "true");
  const tasks = await Promise.allSettled([
    getActiveAlert(),
    getProfile(),
    getNews()
  ]);
  const profile = tasks[1].status === "fulfilled" ? tasks[1].value : null;
  const latitude = Number.isFinite(profile && profile.lat) ? profile.lat : 21.2;
  const longitude = Number.isFinite(profile && profile.lng) ? profile.lng : 78.1;
  const localTasks = await Promise.allSettled([getSafetyScore(latitude, longitude), getWeather(latitude, longitude)]);
  if (profile && profile.name) document.getElementById("greeting-name").textContent = profile.name.split(/\s+/)[0];
  if (tasks[1].status === "rejected") showToast(tasks[1].reason.message, true);
  if (tasks[0].status === "fulfilled") {
    const alert = tasks[0].value;
    const hero = document.getElementById("alert-section");
    if (!alert) {
      hero.classList.add("no-alert");
      document.getElementById("alert-kicker").textContent = "ALL CLEAR";
      document.getElementById("alert-title").textContent = "No active alerts";
      document.getElementById("alert-description").textContent = "There are no high or critical alerts for your area right now. Check back for updates.";
      hero.querySelector(".carousel-dots").hidden = true;
    } else {
      document.getElementById("alert-kicker").textContent = `${String(alert.level || "ACTIVE").toUpperCase()} WEATHER ALERT`;
      document.getElementById("alert-title").textContent = alert.title;
      document.getElementById("alert-description").textContent = alert.description;
    }
  } else showToast(tasks[0].reason.message, true);

  if (localTasks[0].status === "fulfilled" && localTasks[0].value) {
    const { score, level } = localTasks[0].value;
    document.getElementById("safety-score").textContent = score;
    const risk = document.getElementById("safety-risk");
    risk.textContent = `${level} risk`;
    risk.className = `risk-badge ${riskClass(level)}`;
    document.getElementById("score-fill").style.width = scoreBarWidth(score);
  } else if (localTasks[0].status === "rejected") showToast(localTasks[0].reason.message, true);

  if (localTasks[1].status === "fulfilled") {
    const weather = localTasks[1].value;
    document.getElementById("weather-temp").textContent = `${weather.temperature}°C`;
    document.getElementById("weather-condition").innerHTML = `${escapeHtml(weather.condition)} <span>(${escapeHtml(weather.horizon)})</span>`;
    document.getElementById("weather-rain").textContent = weather.rainfall;
    document.getElementById("weather-wind").textContent = weather.windSpeed;
    document.getElementById("weather-pressure").textContent = weather.pressure;
  } else showToast(localTasks[1].reason.message, true);

  if (tasks[2].status === "fulfilled") {
    document.getElementById("recent-news-list").innerHTML = tasks[2].value.slice(0, 3).map(item => renderNewsItem(item, true)).join("");
  } else document.getElementById("recent-news-list").innerHTML = `<p class="empty-state">News updates couldn't be loaded. Please try again later.</p>`;

  initializeMiniMap();
  content.setAttribute("aria-busy", "false");
  if (window.lucide) window.lucide.createIcons();
}

function initializeMiniMap() {
  const container = document.getElementById("mini-map");
  if (!container || !window.L) {
    if (container) container.innerHTML = '<div class="empty-state">The map could not load. Check your internet connection.</div>';
    return;
  }
  const map = L.map(container, { zoomControl: false, attributionControl: true, scrollWheelZoom: false }).setView([21.8, 84.5], 4);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map);
  L.control.zoom({ position: "topright" }).addTo(map);
  getRiskZones("Risk Zones").then(result => {
    const zones = result.zones || [];
    if (L.heatLayer) {
      L.heatLayer(zones.map(zone => [zone.lat, zone.lng, zone.weight]), {
        radius: 32, blur: 25, maxZoom: 7, minOpacity: .3,
        gradient: { 0.2: "#45b878", 0.45: "#e5ca39", 0.68: "#f18c37", 1: "#dc4148" }
      }).addTo(map);
    }
    L.marker([15.2, 88.4], {
      icon: L.divIcon({ className: "cyclone-div-icon", html: '<div class="cyclone-marker"><i data-lucide="tornado"></i></div>' })
    }).addTo(map).bindPopup("<strong>Cyclone alert</strong><br>Eastern Coast");
    if (window.lucide) window.lucide.createIcons();
  }).catch(error => showToast(error.message, true));
}

initializeHome().catch(error => showToast(error.message, true));
