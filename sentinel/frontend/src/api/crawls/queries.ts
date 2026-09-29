import { queryOptions } from "@tanstack/react-query";
import { listCrawls } from "./endpoints";

export const crawls = {
  list: () =>
    queryOptions({
      queryKey: ["crawls"] as const,
      queryFn: ({ signal }) => listCrawls(signal),
    }),
};
