import { request } from "../http";
import type { Overview } from "./types";

/** @package */
export async function getOverview(
  crawl: string | null,
  signal: AbortSignal,
): Promise<Overview> {
  const query = crawl === null ? "" : `?crawl=${encodeURIComponent(crawl)}`;
  const response = await request(`/overview${query}`, { signal });
  return response.json();
}
