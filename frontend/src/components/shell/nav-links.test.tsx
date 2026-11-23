import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { NavLinks } from "./nav-links";

vi.mock("next/navigation", () => ({ usePathname: () => "/incidents/abc-123" }));

describe("NavLinks", () => {
  it("renders all eight sections as links", () => {
    render(<NavLinks />);
    expect(screen.getAllByRole("link")).toHaveLength(8);
  });

  it("marks only the current section with aria-current", () => {
    render(<NavLinks />);
    expect(screen.getByRole("link", { name: "Incident Library" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByRole("link", { name: "Documents" })).not.toHaveAttribute("aria-current");
  });
});
