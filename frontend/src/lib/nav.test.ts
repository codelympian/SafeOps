import { describe, expect, it } from "vitest";

import { isActive, NAV_ITEMS } from "./nav";

describe("navigation", () => {
  it("has the eight sections from the spec, in order", () => {
    expect(NAV_ITEMS.map((item) => item.label)).toEqual([
      "Overview",
      "HSE Assistant",
      "Documents",
      "Incident Library",
      "Job Risk Analysis",
      "Risk Rules",
      "Analytics",
      "Settings",
    ]);
  });

  it("marks a section active for its own path and nested paths only", () => {
    expect(isActive("/documents", "/documents")).toBe(true);
    expect(isActive("/documents/123", "/documents")).toBe(true);
    expect(isActive("/documents-archive", "/documents")).toBe(false);
    expect(isActive("/overview", "/documents")).toBe(false);
  });
});
