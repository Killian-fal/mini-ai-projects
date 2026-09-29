import { request } from "../http";
import type { components } from "../schema";

/** @package */
export async function listCrawls(signal: AbortSignal): Promise<string[]> {
  const response = await request("/crawls", { signal });
  const body: components["schemas"]["Crawls"] = await response.json();
  return body.crawls;
}
