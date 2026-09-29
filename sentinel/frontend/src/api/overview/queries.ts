import { queryOptions } from "@tanstack/react-query";
import { getOverview } from "./endpoints";

export const overview = {
  of: (crawl: string | null) =>
    queryOptions({
      queryKey: ["overview", crawl] as const,
      queryFn: ({ signal }) => getOverview(crawl, signal),
    }),
};
