import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, render, screen } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import { setupServer } from "msw/node";
import { createMemoryRouter, RouterProvider } from "react-router";
import { afterAll, afterEach, beforeAll, expect, it } from "vitest";
import { RunsPage } from "./RunsPage";

const RUN = {
  id: "2026-09-18T13:52|jev-2026.08|0.8",
  started_at: "2026-09-18T13:52:00Z",
  model: "jev-2026.08",
  threshold: 0.8,
  analysed: 4218,
  flagged: 7,
  errors: 2,
  input_tokens: 5_935_000,
  output_tokens: 340_000,
  cost_usd: 249.23,
  duration_ms: 3_821_000,
  median_latency_ms: 1180,
};

const DAILY = Array.from({ length: 30 }, (_, index) => ({
  day: `2026-08-${String(index + 1).padStart(2, "0")}`,
  analysed: index * 10,
  flagged_rate: 0,
}));

let empty = false;

const server = setupServer(
  http.get("http://localhost:8000/api/runs", () =>
    HttpResponse.json({ runs: empty ? [] : [RUN], daily: DAILY }),
  ),
);

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => {
  cleanup();
  empty = false;
});
afterAll(() => server.close());

function renderRuns(): void {
  const router = createMemoryRouter([{ path: "/runs", element: <RunsPage /> }], {
    initialEntries: ["/runs"],
  });
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={client}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  );
}

it("liste les runs et résume la période", async () => {
  renderRuns();

  expect(await screen.findByText("jev-2026.08")).toBeDefined();
  expect(screen.getAllByText(/4\s?218/u).length).toBeGreaterThan(0);
  expect(screen.getByText("$249.23")).toBeDefined();
  expect(screen.getByText("1 h 03")).toBeDefined();
  expect(screen.getByText("5.9/0.34 M")).toBeDefined();
  expect(
    screen.getByText(/1 run · 4\s?218 pages · 7 signalées · \$249\.23/u),
  ).toBeDefined();
});

it("mène à la liste des pages préfiltrée sur le run", async () => {
  renderRuns();

  const line = await screen.findByRole("link", { name: /jev-2026\.08/u });
  expect(line.getAttribute("href")).toBe(`/pages?run=${encodeURIComponent(RUN.id)}`);
});

it("garde les sparklines et explique comment lancer un run quand il n'y en a aucun", async () => {
  empty = true;
  renderRuns();

  expect(await screen.findByText("Aucun run enregistré")).toBeDefined();
  expect(screen.getByText(/python -m sentinel\.run/u)).toBeDefined();
  expect(screen.getByText("Pages analysées par jour")).toBeDefined();
});
