(() => {
  const page = document.body.dataset.page || "home";
  const header = document.getElementById("app-header");
  const sidebar = document.getElementById("app-sidebar");
  if (!header || !sidebar) return;

  header.innerHTML = `
    <header class="topbar">
      <button class="mobile-menu-button icon-button" id="mobile-menu-button" aria-label="Toggle navigation"><i data-lucide="menu"></i></button>
      <a class="brand-mark" href="index.html" aria-label="DARSHAC home"><span class="compass-mark"><i data-lucide="navigation"></i></span><span class="brand-name">DARSHAC<span>.</span></span></a>
      <div class="topbar-search">
        <i data-lucide="search"></i><input id="location-search" type="search" placeholder="Search location..." autocomplete="off" aria-label="Search location">
        <kbd>↵</kbd>
      </div>
      <div class="topbar-actions">
        <button id="notification-button" class="icon-button notification-button" aria-label="Notifications"><i data-lucide="bell"></i><span class="notification-dot"></span></button>
        <a class="topbar-avatar" href="profile.html" aria-label="View profile"><i data-lucide="user-round"></i></a>
      </div>
      <div id="notification-popover" class="notification-popover" hidden><span class="pulse-dot"></span><div><strong>Weather alert</strong><p>Heavy rainfall possible along the Eastern Coast.</p><a href="map.html">View risk map →</a></div></div>
    </header>`;

  const nav = [
    { id: "home", label: "Home", href: "index.html", icon: "house" },
    { id: "map", label: "Map", href: "map.html", icon: "map" },
    { id: "news", label: "News", href: "news.html", icon: "newspaper" },
    { id: "profile", label: "Profile", href: "profile.html", icon: "user-round" }
  ];
  const layers = [
    { id: "Risk Zones", label: "Risk Zones", icon: "shield-alert" },
    { id: "Cyclone", label: "Cyclone", icon: "tornado" },
    { id: "Rainfall", label: "Rainfall", icon: "cloud-rain" },
    { id: "Flood", label: "Flood", icon: "waves" },
    { id: "Wind", label: "Wind", icon: "wind" },
    { id: "Pressure", label: "Pressure", icon: "gauge" }
  ];
  sidebar.className = `sidebar ${page === "map" ? "sidebar-map" : ""}`;
  sidebar.innerHTML = `
    <nav class="primary-nav" aria-label="Main navigation">
      ${nav.map(item => `<a class="nav-item ${page === item.id ? "is-active" : ""}" href="${item.href}" ${page === item.id ? 'aria-current="page"' : ""}><i data-lucide="${item.icon}"></i><span>${item.label}</span></a>`).join("")}
    </nav>
    ${page === "map" ? `<div class="sidebar-divider"></div><p class="sidebar-section-label">MAP LAYERS</p><nav class="layer-nav" aria-label="Map layers">${layers.map((layer, index) => `<button class="layer-nav-item ${index === 0 ? "is-active" : ""}" data-layer="${layer.id}" type="button" aria-pressed="${index === 0}"><i data-lucide="${layer.icon}"></i><span>${layer.label}</span></button>`).join("")}</nav><div class="sidebar-bottom"><span class="online-dot"></span><span>DEMO MODE</span></div>` : `<div class="sidebar-bottom"><span class="sidebar-tip-icon"><i data-lucide="shield-check"></i></span><span>Prepared, not<br>alarmed.</span></div>`}
    <button class="sidebar-close icon-button" id="sidebar-close" aria-label="Close navigation"><i data-lucide="x"></i></button>`;

  function refreshIcons() {
    if (window.lucide) window.lucide.createIcons();
  }
  refreshIcons();
  if (window.lucide) window.addEventListener("load", refreshIcons, { once: true });

  const menuButton = document.getElementById("mobile-menu-button");
  function closeSidebar() {
    document.body.classList.remove("sidebar-open");
    sidebar.classList.remove("is-open");
  }
  menuButton.addEventListener("click", () => {
    const isOpen = sidebar.classList.toggle("is-open");
    document.body.classList.toggle("sidebar-open", isOpen);
  });
  document.getElementById("sidebar-close").addEventListener("click", closeSidebar);
  document.addEventListener("click", event => {
    if (document.body.classList.contains("sidebar-open") &&
        !sidebar.contains(event.target) && !menuButton.contains(event.target)) closeSidebar();
  });
  const notificationButton = document.getElementById("notification-button");
  const notificationPopover = document.getElementById("notification-popover");
  notificationButton.addEventListener("click", () => { notificationPopover.hidden = !notificationPopover.hidden; });
  document.addEventListener("click", event => {
    if (!notificationButton.contains(event.target) && !notificationPopover.contains(event.target)) notificationPopover.hidden = true;
  });
  document.getElementById("location-search").addEventListener("keydown", event => {
    if (event.key !== "Enter") return;
    const query = event.currentTarget.value.trim();
    if (!query) return;
    window.dispatchEvent(new CustomEvent("aegis:search", { detail: { query } }));
    if (page !== "map") window.location.href = `map.html?location=${encodeURIComponent(query)}`;
  });
})();
