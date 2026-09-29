import { request } from "../http";
import type { components } from "../schema";

/** @package */
export async function listRuns(
  signal: AbortSignal,
): Promise<components["schemas"]["Runs"]> {
  const response = await request("/runs", { signal });
  return response.json();
}
