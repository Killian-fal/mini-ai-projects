import { render, screen } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import { setupServer } from "msw/node";
import { afterAll, beforeAll, expect, it } from "vitest";

const server = setupServer(
  http.get("http://localhost:8000/api/crawls", () =>
    HttpResponse.json({ crawls: ["CC-MAIN-2026-34"] }),
  ),
  http.get("http://localhost:8000/api/overview", () =>
    HttpResponse.json({
      stored: 150,
      analysed: 50,
      flagged: 0,
      runs: 3,
      input_tokens: 238_095,
      cost_usd: 0.01,
      threshold: 0.8,
      histogram: Array.from({ length: 20 }, () => 1),
      buckets: [],
      latest_flagged: [],
    }),
  ),
);

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterAll(() => server.close());

it("monte l'application entière sur la vue d'ensemble", async () => {
  window.history.pushState({}, "", "/");
  const { App } = await import("./App");
  render(<App />);

  expect(screen.getByText("Sentinel")).toBeDefined();
  expect(screen.getByRole("link", { name: /Vue d'ensemble/u })).toBeDefined();
  expect(await screen.findByText("Distribution des scores")).toBeDefined();
  expect(await screen.findAllByText("SEUIL 0.80")).toHaveLength(2);
});
