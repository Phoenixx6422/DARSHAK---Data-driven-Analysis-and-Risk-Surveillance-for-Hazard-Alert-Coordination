/*
 * Pure helper functions shared by every Aegis page.
 *
 * Rules for this file: no DOM access, no fetch, no side effects. That is what
 * makes each function easy to unit test with Jest.
 *
 * In the browser these are plain global functions (this file is loaded before
 * the page scripts). In Node/Jest the same functions are exported at the bottom.
 */

/** Escapes characters that could turn user or API text into HTML markup. */
function escapeHtml(value) {
  return String(value == null ? "" : value).replace(/[&<>"']/g, character => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[character]));
}

/** Maps a risk level name to its CSS class, e.g. "High" -> "risk-high". */
function riskClass(level) {
  return `risk-${String(level || "").toLowerCase()}`;
}

/** Width of the SafetyScore bar as a CSS percentage, clamped to 0-100. */
function scoreBarWidth(score) {
  return `${Math.max(0, Math.min(100, score))}%`;
}

/** Email format check: text@text.text with no spaces. */
function emailIsValid(email) {
  return typeof email === "string" && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

/** Phone check: only digits and + ( ) space . - characters, with 9 to 14 digits. */
function phoneIsValid(phone) {
  const text = String(phone == null ? "" : phone);
  const digits = text.replace(/\D/g, "");
  return /^[+()\d\s.-]+$/.test(text) && digits.length >= 7 && digits.length <= 15;
}

/** Validates the required profile fields. Returns an error message, or "" when valid. */
function validateProfile(data) {
  if (!data.name || !data.email || !data.phone || !data.location) return "Name, email, phone number, and location are required.";
  if (!emailIsValid(data.email)) return "Enter a valid email address.";
  if (!phoneIsValid(data.phone)) return "Enter a valid phone number (7–15 digits).";
  return "";
}

/** Map search: centres of known South Asian places, used when a place name is typed. */
const KNOWN_PLACES = {
  india: [22.5, 79], delhi: [28.6, 77.2], mumbai: [19.1, 72.9], kolkata: [22.6, 88.4],
  lucknow: [26.8, 80.9], chennai: [13.1, 80.3], bangladesh: [23.7, 90.4],
  nepal: [28.4, 84.1], pakistan: [30.4, 69.3], "sri lanka": [7.9, 80.7]
};

/** Returns [lat, lng] for the first known place name found in the query, or null. */
function findKnownPlace(query) {
  const text = String(query || "").toLowerCase();
  const match = Object.keys(KNOWN_PLACES).find(place => text.includes(place));
  return match ? KNOWN_PLACES[match] : null;
}

if (typeof module !== "undefined") {
  module.exports = {
    escapeHtml, riskClass, scoreBarWidth, emailIsValid, phoneIsValid,
    validateProfile, findKnownPlace, KNOWN_PLACES
  };
}
