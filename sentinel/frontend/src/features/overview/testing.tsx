import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { createMemoryRouter, RouterProvider } from "react-router";
import type { Overview, PageRow } from "../../api/overview";
import { OverviewPage } from "./OverviewPage";

/** @package */
export const FLAGGED: PageRow = {
  id: "6aac5f19efc74ee9f330f17d",
  url: "https://talent-boost-apply.xyz/jobs/senior-backend-engineer-paris",
  host: "talent-boost-apply.xyz",
  bucket: "hiring",
  crawl: "CC-MAIN-2026-34",
  score: 0.97,
  threshold: 0.8,
  flagged: true,
  error: null,
  input_tokens: 1412,
  output_tokens: 96,
  latency_ms: 1301,
  analysed_at: "2026-09-18T14:02:44",
  html_bytes: 115_405,
  fetched_at: "2026-09-18T13:00:00",
  channels: ["hidden", "comment"],
};

/** @package */
export function overviewBody(over: Partial<Overview> = {}): Overview {
  return {
    stored: 184_920,
    analysed: 152_418,
    flagged: 418,
    runs: 12,
    input_tokens: 214_800_000,
    cost_usd: 9.02,
    threshold: 0.8,
    histogram: [30, 20, 10, 5, 4, 3, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 7],
    buckets: [{ bucket: "hiring", count: 41_280, flagged: 148 }],
    latest_flagged: [FLAGGED],
    ...over,
  };
}

/** @package */
export function renderOverview(path = "/"): void {
  const router = createMemoryRouter([{ path: "/", element: <OverviewPage /> }], {
    initialEntries: [path],
  });
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={client}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  );
}
