/*
 * Unit tests for js/utils.js (pure functions, no DOM).
 *
 * Techniques used (from the Software Testing slides):
 *  - Black-box testing: check output for a given input, without looking inside.
 *  - Equivalence partitioning: one or more test cases per group of similar inputs.
 *  - Boundary-value analysis: test at the edges of each valid range.
 */

const {
  escapeHtml,
  riskClass,
  scoreBarWidth,
  emailIsValid,
  phoneIsValid,
  validateProfile,
  findKnownPlace
} = require("../js/utils");

describe("escapeHtml (black-box, equivalence partitions)", () => {
  test("plain text is returned unchanged", () => {
    expect(escapeHtml("Cyclone alert")).toBe("Cyclone alert");
  });

  test.each([
    ["<script>", "&lt;script&gt;"],
    ['"quoted"', "&quot;quoted&quot;"],
    ["Tom & Jerry", "Tom &amp; Jerry"],
    ["it's", "it&#39;s"]
  ])("escapes special characters in %s", (input, expected) => {
    expect(escapeHtml(input)).toBe(expected);
  });

  test("null and undefined become an empty string", () => {
    expect(escapeHtml(null)).toBe("");
    expect(escapeHtml(undefined)).toBe("");
  });

  test("numbers are converted to text (SafetyScore 72 -> \"72\")", () => {
    expect(escapeHtml(72)).toBe("72");
  });

  test("an injected HTML tag cannot survive as markup", () => {
    const output = escapeHtml('<img src=x onerror="alert(1)">');
    expect(output).not.toContain("<");
    expect(output).toBe("&lt;img src=x onerror=&quot;alert(1)&quot;&gt;");
  });
});

describe("riskClass (black-box, one case per risk level)", () => {
  test.each([
    ["Low", "risk-low"],
    ["Moderate", "risk-moderate"],
    ["High", "risk-high"],
    ["Critical", "risk-critical"]
  ])("%s gives the CSS class %s", (level, expected) => {
    expect(riskClass(level)).toBe(expected);
  });

  test("is case-insensitive", () => {
    expect(riskClass("CRITICAL")).toBe("risk-critical");
  });
});

describe("scoreBarWidth (boundary-value analysis on 0-100)", () => {
  test.each([
    [0, "0%"],      // lower boundary
    [1, "1%"],      // just inside
    [72, "72%"],    // dashboard example
    [99, "99%"],    // just below upper boundary
    [100, "100%"]   // upper boundary
  ])("score %p gives width %s", (score, expected) => {
    expect(scoreBarWidth(score)).toBe(expected);
  });

  test.each([
    [-1, "0%"],     // just below lower boundary is clamped
    [101, "100%"],  // just above upper boundary is clamped
    [500, "100%"]
  ])("out-of-range score %p is clamped to %s", (score, expected) => {
    expect(scoreBarWidth(score)).toBe(expected);
  });
});

describe("emailIsValid (equivalence partitions)", () => {
  test.each([
    ["user@example.com"],
    ["a.b@sub.domain.co.in"]
  ])("valid address %s is accepted", email => {
    expect(emailIsValid(email)).toBe(true);
  });

  test.each([
    ["userexample.com", "missing @"],
    ["user@", "missing domain"],
    ["user@domain", "missing dot in domain"],
    ["us er@example.com", "contains a space"],
    ["", "empty string"]
  ])("invalid address (%s: %s) is rejected", email => {
    expect(emailIsValid(email)).toBe(false);
  });

  test("non-string input is rejected", () => {
    expect(emailIsValid(null)).toBe(false);
    expect(emailIsValid(undefined)).toBe(false);
  });
});

describe("phoneIsValid (boundary-value analysis on 7-15 digits)", () => {
  test("accepts a number with country code and spaces", () => {
    expect(phoneIsValid("+91 98765 43210")).toBe(true);
  });

  test("accepts a 10-digit number", () => {
    expect(phoneIsValid("9876543210")).toBe(true);
  });

  test("accepts punctuation such as brackets and dashes", () => {
    expect(phoneIsValid("+1 (555) 123-4567")).toBe(true);
  });

  test("lower boundary: 6 digits rejected, 7 digits accepted", () => {
    expect(phoneIsValid("123456")).toBe(false);
    expect(phoneIsValid("1234567")).toBe(true);
  });

  test("upper boundary: 15 digits accepted, 16 digits rejected", () => {
    expect(phoneIsValid("1".repeat(15))).toBe(true);
    expect(phoneIsValid("1".repeat(16))).toBe(false);
  });

  test("letters are rejected", () => {
    expect(phoneIsValid("98765abcde")).toBe(false);
  });

  test("empty and null input are rejected", () => {
    expect(phoneIsValid("")).toBe(false);
    expect(phoneIsValid(null)).toBe(false);
  });
});

describe("validateProfile (branch coverage)", () => {
  const valid = {
    name: "Sanskar Dave",
    email: "user@example.com",
    phone: "+91 98765 43210",
    location: "Lucknow, Uttar Pradesh"
  };

  test("returns an empty string when every field is valid", () => {
    expect(validateProfile(valid)).toBe("");
  });

  test.each(["name", "email", "phone", "location"])(
    "a missing %s gives the required-fields message",
    field => {
      const data = { ...valid, [field]: "" };
      expect(validateProfile(data)).toBe("Name, email, phone number, and location are required.");
    }
  );

  test("an invalid email gives the email message", () => {
    expect(validateProfile({ ...valid, email: "not-an-email" })).toBe("Enter a valid email address.");
  });

  test("an invalid phone gives the phone message", () => {
    expect(validateProfile({ ...valid, phone: "abc" })).toBe("Enter a valid phone number (7–15 digits).");
  });
});

describe("findKnownPlace (map search, equivalence partitions)", () => {
  test("a known city returns its centre", () => {
    expect(findKnownPlace("Lucknow")).toEqual([26.8, 80.9]);
  });

  test("matching ignores case and surrounding spaces", () => {
    expect(findKnownPlace("  CHENNAI  ")).toEqual([13.1, 80.3]);
  });

  test("a place name inside a longer phrase is found", () => {
    expect(findKnownPlace("near Kolkata city")).toEqual([22.6, 88.4]);
  });

  test("a multi-word place is matched", () => {
    expect(findKnownPlace("Sri Lanka")).toEqual([7.9, 80.7]);
  });

  test("an unknown place returns null", () => {
    expect(findKnownPlace("Atlantis")).toBeNull();
  });

  test("empty and null queries return null", () => {
    expect(findKnownPlace("")).toBeNull();
    expect(findKnownPlace(null)).toBeNull();
  });
});
