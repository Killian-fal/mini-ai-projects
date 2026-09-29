import type { components, operations } from "../schema";

export type PageRow = components["schemas"]["PageRow"];
export type PageList = components["schemas"]["PageList"];
export type PageDetail = components["schemas"]["PageDetail"];
export type Detection = components["schemas"]["Detection"];
export type PageRequest = components["schemas"]["PageRequest"]["request"];
export type SortField = components["schemas"]["SortField"];
export type Order = components["schemas"]["Order"];
export type PageQuery = NonNullable<operations["list_pages"]["parameters"]["query"]>;
