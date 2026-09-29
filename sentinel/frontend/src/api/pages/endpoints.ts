import { request } from "../http";
import type { PageDetail, PageList, PageQuery, PageRequest } from "./types";

function search(query: PageQuery): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null) {
      continue;
    }
    for (const one of Array.isArray(value) ? value : [value]) {
      params.append(key, String(one));
    }
  }
  return params.toString();
}

/** @package */
export async function listPages(
  query: PageQuery,
  signal: AbortSignal,
): Promise<PageList> {
  const response = await request(`/pages?${search(query)}`, { signal });
  return response.json();
}

/** @package */
export async function getPage(id: string, signal: AbortSignal): Promise<PageDetail> {
  const response = await request(`/pages/${id}`, { signal });
  return response.json();
}

/** @package */
export async function getPageHtml(id: string, signal: AbortSignal): Promise<string> {
  const response = await request(`/pages/${id}/html`, { signal });
  const body: { html: string } = await response.json();
  return body.html;
}

/** @package */
export async function getPageRequest(
  id: string,
  signal: AbortSignal,
): Promise<PageRequest> {
  const response = await request(`/pages/${id}/request`, { signal });
  const body: { request: PageRequest } = await response.json();
  return body.request;
}
