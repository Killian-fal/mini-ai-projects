import { queryOptions, useQuery } from "@tanstack/react-query";
import { getPage, getPageHtml, getPageRequest, listPages } from "./endpoints";
import type { PageQuery } from "./types";

export const pages = {
  list: (query: PageQuery) =>
    queryOptions({
      queryKey: ["pages", query] as const,
      queryFn: ({ signal }) => listPages(query, signal),
    }),
  detail: (id: string) =>
    queryOptions({
      queryKey: ["page", id] as const,
      queryFn: ({ signal }) => getPage(id, signal),
    }),
  // A page's html never changes: switching tabs back and forth must not refetch it.
  html: (id: string) =>
    queryOptions({
      queryKey: ["page-html", id] as const,
      queryFn: ({ signal }) => getPageHtml(id, signal),
      staleTime: Number.POSITIVE_INFINITY,
    }),
  // The request sent to Jev never changes either: reopening the modal does not refetch it.
  request: (id: string) =>
    queryOptions({
      queryKey: ["page-request", id] as const,
      queryFn: ({ signal }) => getPageRequest(id, signal),
      staleTime: Number.POSITIVE_INFINITY,
    }),
};

export function usePageRequest(id: string, enabled: boolean) {
  return useQuery({ ...pages.request(id), enabled });
}
