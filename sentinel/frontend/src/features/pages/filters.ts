import type { Order, PageQuery, SortField } from "../../api/pages";

/** @package */
export const SIZE = 50;

const SORTS: SortField[] = ["score", "analysed_at", "html_bytes"];

/** @package */
export const SORT_LABEL: Record<SortField, string> = {
  score: "score",
  html_bytes: "taille",
  analysed_at: "date",
};

function one(params: URLSearchParams, key: string, fallback: string): string {
  return params.get(key) ?? fallback;
}

/**
 * Url parameter names are the API's: a `?run=…` coming from Runs
 * crosses the screen without translation.
 */
/** @package */
export function toQuery(params: URLSearchParams): PageQuery {
  const sort = one(params, "sort", "score");
  const min = params.get("min_score");
  return {
    q: params.get("q"),
    bucket: params.getAll("bucket"),
    crawl: params.get("crawl"),
    run: params.get("run"),
    flagged_only: params.get("flagged_only") === "1",
    with_error: params.get("with_error") === "1",
    min_score: min === null ? null : Number(min),
    sort: SORTS.includes(sort as SortField) ? (sort as SortField) : "score",
    order: one(params, "order", "desc") === "asc" ? "asc" : "desc",
    page: Math.max(1, Number(one(params, "page", "1")) || 1),
    size: SIZE,
  };
}

/** Any filter change goes back to page 1; `page` only changes on its own. */
/** @package */
export function withChange(
  params: URLSearchParams,
  changes: Record<string, string | string[] | null>,
): URLSearchParams {
  const next = new URLSearchParams(params);
  for (const [key, value] of Object.entries(changes)) {
    next.delete(key);
    for (const one of value === null ? [] : [value].flat()) {
      next.append(key, one);
    }
  }
  if (!("page" in changes)) {
    next.delete("page");
  }
  return next;
}

/** @package */
export function withSort(params: URLSearchParams, field: SortField): URLSearchParams {
  const current = toQuery(params);
  const order: Order =
    current.sort === field && current.order === "desc" ? "asc" : "desc";
  return withChange(params, { sort: field, order });
}

/** @package */
export function reset(params: URLSearchParams): URLSearchParams {
  return withChange(params, {
    q: null,
    bucket: null,
    crawl: null,
    run: null,
    flagged_only: null,
    with_error: null,
    min_score: null,
  });
}
