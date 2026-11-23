import { describe, expect, it } from "vitest";

import { errorMessage } from "./client";

describe("errorMessage", () => {
  it("uses a string detail as-is", () => {
    expect(errorMessage({ detail: "Email already registered" })).toBe("Email already registered");
  });

  it("names the field from a FastAPI validation error", () => {
    const detail = [{ loc: ["body", "password"], msg: "String should have at least 10 characters" }];
    expect(errorMessage({ detail })).toBe("password: String should have at least 10 characters");
  });

  it("falls back for unknown shapes", () => {
    expect(errorMessage(undefined, "Login failed")).toBe("Login failed");
    expect(errorMessage({ nope: true })).toBe("Something went wrong");
  });
});
