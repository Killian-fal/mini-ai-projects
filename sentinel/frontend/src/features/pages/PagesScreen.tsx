import * as stylex from "@stylexjs/stylex";
import type { PageList, PageQuery, PageRow, SortField } from "../../api/pages";
import { FilterBar } from "./FilterBar";
import { PageTable } from "./PageTable";
import { Pagination } from "./Pagination";

const styles = stylex.create({
  body: {
    display: "flex",
    flexDirection: "column",
    gap: 18,
    padding: {
      default: "20px 32px 72px",
      "@media (max-width: 640px)": "20px 20px 64px",
    },
  },
});

export function PagesScreen({
  list,
  query,
  crawls,
  buckets,
  hrefOf,
  onChange,
  onReset,
  onSort,
  onPage,
}: {
  list: PageList;
  query: PageQuery;
  crawls: string[];
  buckets: string[];
  hrefOf: (page: PageRow) => string;
  onChange: (changes: Record<string, string | string[] | null>) => void;
  onReset: () => void;
  onSort: (field: SortField) => void;
  onPage: (page: number) => void;
}) {
  return (
    <div {...stylex.props(styles.body)}>
      <FilterBar
        query={query}
        crawls={crawls}
        buckets={buckets}
        onChange={onChange}
        onReset={onReset}
      />
      <PageTable rows={list.items} query={query} hrefOf={hrefOf} onSort={onSort} />
      <Pagination
        page={query.page ?? 1}
        perPage={query.size ?? list.items.length}
        total={list.total}
        onPage={onPage}
      />
    </div>
  );
}
