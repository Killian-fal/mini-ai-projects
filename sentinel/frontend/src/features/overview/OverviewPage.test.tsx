import { cleanup, fireEvent, screen } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import { setupServer } from "msw/node";
import { afterAll, afterEach, beforeAll, expect, it } from "vitest";
import { overviewBody, renderOverview } from "./testing";

const asked: string[] = [];

const server = setupServer(
  http.get("http://localhost:8000/api/crawls", () =>
    HttpResponse.json({ crawls: ["CC-MAIN-2026-34", "CC-MAIN-2026-30"] }),
  ),
  http.get("http://localhost:8000/api/overview", ({ request }) => {
    const crawl = new URL(request.url).searchParams.get("crawl");
    asked.push(crawl ?? "tous");
    return HttpResponse.json(
      crawl === "CC-MAIN-2026-30"
        ? overviewBody({ analysed: 58_090, flagged: 0, latest_flagged: [] })
        : overviewBody(),
    );
  }),
);

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => {
  cleanup();
  asked.length = 0;
});
afterAll(() => server.close());

const spaces = (text: string) => text.replace(/\s/gu, " ");

it("montre les chiffres clés et les dernières pages signalées", async () => {
  renderOverview();

  expect(await screen.findByText(/184\s920/u)).toBeDefined();
  expect(screen.getByText(/152\s418/u)).toBeDefined();
  expect(screen.getByText("$9.02")).toBeDefined();
  expect(screen.getByText("talent-boost-apply.xyz")).toBeDefined();
  expect(screen.getByText("0.97")).toBeDefined();
  expect(screen.getByText("[hidden]")).toBeDefined();
  expect(
    screen.getByRole("link", { name: /talent-boost-apply/u }).getAttribute("href"),
  ).toBe("/pages/6aac5f19efc74ee9f330f17d");
});

it("annonce l'absence de détection quand rien n'est signalé", async () => {
  renderOverview("/?crawl=CC-MAIN-2026-30");

  const empty = await screen.findByText(/Aucune injection détectée/u);
  expect(spaces(empty.textContent ?? "")).toBe(
    "Aucune injection détectée sur 58 090 pages",
  );
  expect(screen.queryByText("talent-boost-apply.xyz")).toBeNull();
});

it("rejoue la requête sur le crawl choisi", async () => {
  renderOverview();
  await screen.findByText("talent-boost-apply.xyz");

  fireEvent.change(screen.getByLabelText("Crawl"), {
    target: { value: "CC-MAIN-2026-30" },
  });

  await screen.findByText(/Aucune injection détectée/u);
  expect(asked).toEqual(["tous", "CC-MAIN-2026-30"]);
});
