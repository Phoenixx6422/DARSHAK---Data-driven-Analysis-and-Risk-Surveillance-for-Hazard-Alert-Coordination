(() => {
  const form = document.getElementById("profile-form");
  const toast = document.getElementById("toast");
  const dialog = document.getElementById("family-dialog");
  let profile = null;
  let locationMap = null;
  let locationMarker = null;

  function showToast(message, isError) {
    toast.textContent = message;
    toast.classList.toggle("is-error", Boolean(isError));
    toast.classList.add("is-visible");
    window.clearTimeout(showToast.timeout);
    showToast.timeout = window.setTimeout(() => toast.classList.remove("is-visible"), 3200);
  }

  function showFormError(message) {
    const error = document.getElementById("profile-form-error");
    error.textContent = message;
    error.hidden = !message;
  }

  function setEditable(field, editable) {
    const display = document.getElementById(field === "name" ? "profile-name-display" : `${field}-display`);
    const input = document.getElementById(`${field}-input`);
    if (display) display.hidden = editable;
    if (input) input.hidden = !editable;
    const button = document.querySelector(`[data-edit="${field}"]`);
    if (button) button.textContent = editable ? "Done" : "Edit";
    document.getElementById("save-profile-button").hidden = false;
    showFormError("");
  }

  function setAllEditable() {
    ["phone", "email", "name", "location"].forEach(field => setEditable(field, true));
    ["emergency-contact", "blood-group", "other-info"].forEach(id => {
      document.getElementById(`${id}-display`).hidden = true;
      document.getElementById(`${id}-input`).hidden = false;
    });
    document.getElementById("edit-profile-button").innerHTML = '<i data-lucide="check"></i> Editing';
    if (window.lucide) window.lucide.createIcons();
  }

  function renderFamilyContacts(contacts) {
    const container = document.getElementById("family-list");
    if (!contacts || !contacts.length) {
      container.innerHTML = '<span class="field-value">No family contacts added</span>';
      return;
    }
    container.innerHTML = contacts.map(contact => `<span class="family-contact-chip">${escapeHtml(contact.name)} <span>${escapeHtml(contact.phone)}</span></span>`).join("");
  }

  function renderProfile(data) {
    profile = data;
    [
      ["profile-name-display", "profile-name-input"],
      ["phone-display", "phone-input"],
      ["email-display", "email-input"],
      ["location-display", "location-input"],
      ["emergency-contact-display", "emergency-contact-input"],
      ["blood-group-display", "blood-group-input"],
      ["other-info-display", "other-info-input"]
    ].forEach(([displayId, inputId]) => {
      document.getElementById(displayId).hidden = false;
      document.getElementById(inputId).hidden = true;
    });
    document.querySelectorAll(".edit-field").forEach(button => { button.textContent = "Edit"; });
    document.getElementById("edit-emergency-button").textContent = "Edit";
    document.getElementById("edit-blood-button").textContent = "Edit";
    document.getElementById("edit-other-button").textContent = "Edit";
    document.getElementById("edit-profile-button").innerHTML = '<i data-lucide="pencil"></i> Edit Profile';
    document.getElementById("save-profile-button").hidden = true;
    document.getElementById("profile-name-display").textContent = data.name || "";
    document.getElementById("profile-email-display").textContent = data.email || "";
    document.getElementById("phone-display").textContent = data.phone || "";
    document.getElementById("email-display").textContent = data.email || "";
    document.getElementById("location-display").textContent = data.location || "";
    document.getElementById("profile-name-input").value = data.name || "";
    document.getElementById("phone-input").value = data.phone || "";
    document.getElementById("email-input").value = data.email || "";
    document.getElementById("location-input").value = data.location || "";
    document.getElementById("emergency-contact-display").textContent = data.emergencyContact || "";
    document.getElementById("emergency-contact-input").value = (data.emergencyContact || "").replace(/^Emergency contact:\s*/i, "");
    document.getElementById("blood-group-display").textContent = data.bloodGroup || "Unknown";
    document.getElementById("blood-group-input").value = data.bloodGroup || "Unknown";
    document.getElementById("other-info-display").textContent = data.otherInfo || "—";
    document.getElementById("other-info-input").value = data.otherInfo || "";
    ["smsAlerts", "emailAlerts", "appAlerts"].forEach(key => {
      form.elements[key].checked = Boolean(data.preferences && data.preferences[key]);
    });
    renderFamilyContacts(data.familyContacts || []);
    initializeLocationMap(data.lat || 26.8467, data.lng || 80.9462);
  }

  function initializeLocationMap(lat, lng) {
    const container = document.getElementById("location-preview");
    if (!window.L) {
      container.innerHTML = '<div class="empty-state">Location preview is unavailable.</div>';
      return;
    }
    if (!locationMap) {
      locationMap = L.map(container, { zoomControl: false, attributionControl: true, dragging: false, scrollWheelZoom: false }).setView([lat, lng], 11);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 18,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      }).addTo(locationMap);
      locationMarker = L.marker([lat, lng]).addTo(locationMap);
    } else {
      locationMap.setView([lat, lng], 11);
      locationMarker.setLatLng([lat, lng]);
    }
    window.setTimeout(() => locationMap.invalidateSize(), 100);
  }

  function buildUpdatedProfile() {
    return {
      ...profile,
      name: document.getElementById("profile-name-input").hidden ? profile.name : document.getElementById("profile-name-input").value.trim(),
      phone: document.getElementById("phone-input").hidden ? profile.phone : document.getElementById("phone-input").value.trim(),
      email: document.getElementById("email-input").hidden ? profile.email : document.getElementById("email-input").value.trim(),
      location: document.getElementById("location-input").hidden ? profile.location : document.getElementById("location-input").value.trim(),
      emergencyContact: document.getElementById("emergency-contact-input").hidden ? profile.emergencyContact : `Emergency contact: ${document.getElementById("emergency-contact-input").value.trim()}`,
      bloodGroup: document.getElementById("blood-group-input").hidden ? profile.bloodGroup : document.getElementById("blood-group-input").value,
      otherInfo: document.getElementById("other-info-input").hidden ? profile.otherInfo : document.getElementById("other-info-input").value.trim(),
      preferences: {
        smsAlerts: form.elements.smsAlerts.checked,
        emailAlerts: form.elements.emailAlerts.checked,
        appAlerts: form.elements.appAlerts.checked
      }
    };
  }

  function revealFamilyContacts() {
    const container = document.getElementById("family-contact-fields");
    container.innerHTML = "";
    (profile.familyContacts || []).forEach(contact => addFamilyRow(contact.name, contact.phone));
    if (!container.children.length) addFamilyRow("", "");
    dialog.showModal();
  }

  function addFamilyRow(name, phone) {
    const container = document.getElementById("family-contact-fields");
    const row = document.createElement("div");
    row.className = "family-entry";
    row.innerHTML = `<input type="text" name="familyName" maxlength="70" placeholder="Name" aria-label="Family contact name" value="${escapeHtml(name)}"><input type="tel" name="familyPhone" maxlength="24" placeholder="Phone number" aria-label="Family contact phone" value="${escapeHtml(phone)}"><button type="button" aria-label="Remove contact"><i data-lucide="trash-2"></i></button>`;
    row.querySelector("button").addEventListener("click", () => row.remove());
    container.appendChild(row);
    if (window.lucide) window.lucide.createIcons();
  }

  document.getElementById("edit-profile-button").addEventListener("click", setAllEditable);
  document.querySelectorAll(".edit-field").forEach(button => button.addEventListener("click", () => {
    const field = button.dataset.edit;
    const input = document.getElementById(`${field}-input`);
    setEditable(field, input.hidden);
  }));
  document.getElementById("change-location-button").addEventListener("click", () => {
    const input = document.getElementById("location-input");
    input.hidden = !input.hidden;
    document.getElementById("location-display").hidden = !input.hidden;
    document.getElementById("save-profile-button").hidden = false;
    if (!input.hidden) input.focus();
  });
  [
    ["edit-emergency-button", "emergency-contact"],
    ["edit-blood-button", "blood-group"],
    ["edit-other-button", "other-info"]
  ].forEach(([buttonId, field]) => {
    document.getElementById(buttonId).addEventListener("click", () => {
      const input = document.getElementById(`${field}-input`);
      const display = document.getElementById(`${field}-display`);
      input.hidden = !input.hidden;
      display.hidden = !input.hidden;
      document.getElementById("save-profile-button").hidden = false;
      if (!input.hidden) input.focus();
    });
  });
  form.querySelectorAll('input[type="checkbox"]').forEach(input => input.addEventListener("change", () => {
    document.getElementById("save-profile-button").hidden = false;
  }));
  form.addEventListener("submit", async event => {
    event.preventDefault();
    const updated = buildUpdatedProfile();
    const validationMessage = validateProfile(updated);
    if (validationMessage) {
      showFormError(validationMessage);
      return;
    }
    try {
      profile = await saveProfile(updated);
      renderProfile(profile);
      document.getElementById("save-profile-button").hidden = true;
      showFormError("");
      document.getElementById("edit-profile-button").innerHTML = '<i data-lucide="pencil"></i> Edit Profile';
      if (window.lucide) window.lucide.createIcons();
      showToast("Profile details saved for this demo.");
    } catch (error) {
      showFormError(error.message);
    }
  });

  document.getElementById("manage-family-button").addEventListener("click", revealFamilyContacts);
  document.getElementById("add-family-contact").addEventListener("click", () => addFamilyRow("", ""));
  document.getElementById("save-family-button").addEventListener("click", async () => {
    const rows = [...document.querySelectorAll(".family-entry")];
    const contacts = [];
    for (const row of rows) {
      const name = row.querySelector('[name="familyName"]').value.trim();
      const phone = row.querySelector('[name="familyPhone"]').value.trim();
      if (!name && !phone) continue;
      if (!name || !phone || !phoneIsValid(phone)) {
        showToast("Enter a name and a valid phone number for every family contact.", true);
        return;
      }
      contacts.push({ name, phone });
    }
    try {
      profile = await saveProfile({ ...profile, familyContacts: contacts });
      renderFamilyContacts(profile.familyContacts);
      dialog.close();
      showToast("Family contacts saved for this demo.");
    } catch (error) {
      showToast(error.message, true);
    }
  });

  document.getElementById("contact-form-toggle").addEventListener("click", () => {
    const fields = document.getElementById("contact-form-fields");
    fields.hidden = !fields.hidden;
  });
  document.getElementById("send-message-button").addEventListener("click", () => {
    const message = document.getElementById("contact-message");
    if (!message.value.trim()) {
      message.focus();
      showToast("Please enter a message before sending.", true);
      return;
    }
    message.value = "";
    document.getElementById("contact-form-fields").hidden = true;
    showToast("Your demo message has been received.");
  });

  form.setAttribute("aria-busy", "true");
  getProfile().then(renderProfile).catch(error => showToast(error.message, true)).finally(() => form.setAttribute("aria-busy", "false"));
  if (window.lucide) window.lucide.createIcons();
})();
