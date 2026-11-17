/**
 * @jest-environment jsdom
 * @jest-environment-options {"url": "file:///C:/aegis/index.html"}
 */

/*
 * Branch test: when a page is opened by double-clicking index.html (file://),
 * browsers block fetch() for local files, so api.js must use its built-in
 * fallback data instead of calling fetch at all.
 */

const fs = require("fs");
const path = require("path");

describe("api.js when opened from file:// (branch: built-in fallback data)", () => {
  beforeEach(() => {
    jest.resetModules();
    global.fetch = jest.fn();
  });

  test("the page is running under file:// in this test", () => {
    expect(window.location.protocol).toBe("file:");
  });

  test("getActiveAlert uses the built-in fallback and never calls fetch", async () => {
    const api = require("../js/api");
    const alert = await api.getActiveAlert();
    expect(alert.title).toBe("Cyclone Alert");
    expect(global.fetch).not.toHaveBeenCalled();
  });

  test("the fallback weather data matches data/mock/weather.json (no drift)", async () => {
    const api = require("../js/api");
    const fromFile = JSON.parse(
      fs.readFileSync(path.join(__dirname, "..", "data", "mock", "weather.json"), "utf8")
    );
    expect(await api.getWeather(26.8, 80.9)).toEqual(fromFile);
  });
});
