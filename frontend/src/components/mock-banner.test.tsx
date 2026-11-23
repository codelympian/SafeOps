import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { MockBanner } from "./mock-banner";

const useSystemInfo = vi.fn();
vi.mock("@/lib/session", () => ({ useSystemInfo: () => useSystemInfo() }));

const info = { app_env: "development", llm_provider: "mock", embedding_model: "bge" };

describe("MockBanner", () => {
  beforeEach(() => useSystemInfo.mockReset());

  it("is visible when the mock provider is active", () => {
    useSystemInfo.mockReturnValue({ data: { ...info, mock_mode: true } });
    render(<MockBanner />);
    expect(screen.getByRole("status")).toHaveTextContent(/mock ai provider active/i);
  });

  it("is hidden with a real provider", () => {
    useSystemInfo.mockReturnValue({ data: { ...info, llm_provider: "anthropic", mock_mode: false } });
    render(<MockBanner />);
    expect(screen.queryByRole("status")).toBeNull();
  });

  it("is hidden while system info is loading", () => {
    useSystemInfo.mockReturnValue({ data: undefined });
    render(<MockBanner />);
    expect(screen.queryByRole("status")).toBeNull();
  });
});
