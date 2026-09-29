import { cleanup, fireEvent, screen } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import { setupServer } from "msw/node";
import { afterAll, afterEach, beforeAll, expect, it } from "vitest";
import { renderPages, row } from "./testing";

const asked: URLSearchParams[] = [];

const server = setupServer(
  http.get("http://localhost:8000/api/crawls", () =>
    HttpResponse.json({ crawls: ["CC-MAIN-2026-34"] }),
  ),
  http.get("http://localhost:8000/api/overview", () =>
    // only the categories matter here: this screen does not read the rest of the overview
    HttpResponse.json({
      buckets: [
        { bucket: "reputation", count: 48_000, flagged: 2 },
        { bucket: "hiring", count: 6_600, flagged: 148 },
        { bucket: "other", count: 9_451, flagged: 0 },
      ],
    }),
  ),
  http.get("http://localhost:8000/api/pages", ({ request }) => {
    const params = new URL(request.url).searchParams;
    asked.push(params);
    return HttpResponse.json({
      items:
        params.get("q") === "rien" ? [] : [row(), row({ id: "b", host: "b.test" })],
      total: 1284,
      flagged_total: 12,
    });
  }),
  http.get("http://localhost:8000/api/pages/:id", () =>
    HttpResponse.json({ detail: "page introuvable" }, { status: 404 }),
  ),
);

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => {
  cleanup();
  asked.length = 0;
});
afterAll(() => server.close());

const last = () => asked[asked.length - 1];

it("affiche le compte, les lignes et le tri par défaut", async () => {
  renderPages("/pages");

  expect(await screen.findByText(/1\s?284 pages, 12 signalées/u)).toBeDefined();
  expect(screen.getByText("talent-boost-apply.xyz")).toBeDefined();
  expect(screen.getAllByText("0.96")).toHaveLength(2);
  expect(last()?.get("sort")).toBe("score");
  expect(last()?.get("order")).toBe("desc");
  expect(last()?.get("size")).toBe("50");
});

it("envoie les filtres choisis au serveur", async () => {
  renderPages("/pages");
  await screen.findByText("talent-boost-apply.xyz");

  fireEvent.change(screen.getByLabelText("Filtrer sur l'url"), {
    target: { value: "rien" },
  });
  await screen.findByText("Aucune page ne correspond à ces filtres");
  expect(last()?.get("q")).toBe("rien");

  // "other" was not in the front's hardcoded list: it only comes from the database
  fireEvent.click(screen.getByRole("button", { name: "other" }));
  await screen.findByText("Aucune page ne correspond à ces filtres");
  expect(last()?.getAll("bucket")).toEqual(["other"]);
});

it("inverse l'ordre au second clic sur une colonne triable", async () => {
  renderPages("/pages");
  await screen.findByText("talent-boost-apply.xyz");

  fireEvent.click(screen.getByRole("button", { name: /Taille/u }));
  await screen.findByText("talent-boost-apply.xyz");
  expect([last()?.get("sort"), last()?.get("order")]).toEqual(["html_bytes", "desc"]);

  fireEvent.click(screen.getByRole("button", { name: /Taille/u }));
  await screen.findByText("talent-boost-apply.xyz");
  expect([last()?.get("sort"), last()?.get("order")]).toEqual(["html_bytes", "asc"]);
});

it("ouvre le détail au clic sur une ligne en gardant les filtres", async () => {
  renderPages("/pages?crawl=CC-MAIN-2026-34");
  const line = await screen.findByRole("link", { name: /talent-boost-apply/u });

  expect(line.getAttribute("href")).toBe(
    "/pages/6aac5f19efc74ee9f330f17d?crawl=CC-MAIN-2026-34",
  );
  fireEvent.click(line);
  expect(await screen.findByText("Cette page est introuvable")).toBeDefined();
});
