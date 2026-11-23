import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithQuery } from "@/test/render";

import { LoginForm } from "./login-form";

const replace = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace }) }));

const post = vi.fn();
vi.mock("@/lib/api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/lib/api/client")>();
  return { ...actual, api: { POST: (...args: unknown[]) => post(...args) } };
});

async function submit(email: string, password: string) {
  const user = userEvent.setup();
  await user.type(screen.getByLabelText("Email"), email);
  await user.type(screen.getByLabelText("Password"), password);
  await user.click(screen.getByRole("button", { name: "Sign in" }));
}

describe("LoginForm", () => {
  beforeEach(() => {
    post.mockReset();
    replace.mockReset();
  });

  it("shows the API's error message on bad credentials and stays on the page", async () => {
    post.mockResolvedValue({
      data: undefined,
      error: { detail: "Invalid email or password" },
      response: { status: 401, ok: false },
    });
    renderWithQuery(<LoginForm />);
    await submit("a@example.com", "wrong-password");

    expect(await screen.findByText("Invalid email or password")).toBeInTheDocument();
    expect(replace).not.toHaveBeenCalled();
  });

  it("sends credentials and navigates to the overview on success", async () => {
    post.mockResolvedValue({
      data: {
        user: { id: "u1", email: "a@example.com", full_name: "A", role: "engineer", is_active: true },
        organization: { id: "o1", name: "Org", slug: "org" },
        csrf_token: "csrf-1",
      },
      error: undefined,
      response: { status: 200, ok: true },
    });
    renderWithQuery(<LoginForm />);
    await submit("a@example.com", "right-password");

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/overview"));
    expect(post).toHaveBeenCalledWith("/auth/login", {
      body: { email: "a@example.com", password: "right-password" },
    });
  });
});
