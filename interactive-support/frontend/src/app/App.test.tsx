import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { renderApp } from "../test/renderApp";

describe("App", () => {
  it("mounts the support page on the welcome screen", async () => {
    renderApp();
    expect(await screen.findByRole("heading", { level: 1 })).toBeDefined();
    expect(screen.getByRole("textbox", { name: /expliquez-nous/i })).toBeDefined();
  });

  it("sends an unknown address back to the welcome screen", async () => {
    const { router } = renderApp("/nowhere");
    expect(await screen.findByRole("textbox", { name: /expliquez-nous/i })).toBeDefined();
    expect(router.state.location.pathname).toBe("/");
  });
});
