(() => {
  const list = document.getElementById("news-list");
  const filter = document.getElementById("news-filter");
  const count = document.getElementById("news-count");
  let newsItems = [];

  function render() {
    const selected = filter.value;
    const visible = selected === "all" ? newsItems : newsItems.filter(item => item.type === selected);
    count.textContent = `${visible.length} update${visible.length === 1 ? "" : "s"}`;
    if (!visible.length) {
      list.innerHTML = '<div class="empty-state">No updates match this filter.</div>';
      return;
    }
    list.innerHTML = visible.map(item => `<article class="news-item">
      <img class="news-thumb" src="${escapeHtml(item.image)}" alt="" loading="lazy">
      <div class="news-item-content"><h3>${escapeHtml(item.headline)}</h3>
        <p class="news-summary">${escapeHtml(item.summary || "")}</p>
        <div class="news-meta"><span class="news-type">${escapeHtml(item.type)}</span><span class="meta-dot"></span><span class="news-source">${escapeHtml(item.source)}</span><span class="meta-dot"></span><span>${escapeHtml(item.time)}</span></div>
      </div>
    </article>`).join("");
    list.querySelectorAll("img").forEach(image => image.addEventListener("error", () => {
      image.src = "https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=360&q=70";
    }, { once: true }));
  }

  filter.addEventListener("change", render);
  list.setAttribute("aria-busy", "true");
  getNews().then(items => {
    newsItems = items;
    render();
  }).catch(error => {
    list.innerHTML = `<div class="empty-state">${escapeHtml(error.message)}</div>`;
  }).finally(() => list.setAttribute("aria-busy", "false"));
})();
