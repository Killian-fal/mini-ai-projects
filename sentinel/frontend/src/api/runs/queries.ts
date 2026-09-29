import { queryOptions } from "@tanstack/react-query";
import { listRuns } from "./endpoints";

export const runs = {
  list: () =>
    queryOptions({
      queryKey: ["runs"] as const,
      queryFn: ({ signal }) => listRuns(signal),
    }),
};
