import * as stylex from "@stylexjs/stylex";
import { useQuery } from "@tanstack/react-query";
import type { ReactElement } from "react";
import { useSearchParams } from "react-router";
import { crawls } from "../../api/crawls";
import { overview } from "../../api/overview";
import { pages } from "../../api/pages";
import { count } from "../../ui/format";
import { Notice } from "../../ui/Notice";
import { screen } from "../../ui/screen";
import { TopBar } from "../../ui/TopBar";
import { color, font } from "../../ui/tokens.stylex";
import { reset, toQuery, withChange, withSort } from "./filters";
import { PagesScreen } from "./PagesScreen";

const styles = stylex.create({
  summary: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.09em",
    textTransform: "uppercase",
    color: color.textDim,
    whiteSpace: "nowrap",
  },
});

export function PagesPage(): ReactElement {
  const [params, setParams] = useSearchParams();
  const query = toQuery(params);
  const known = useQuery(crawls.list());
  // the filterable categories are the ones in the database, not a hardcoded list
  const stats = useQuery(overview.of(query.crawl ?? null));
  const list = useQuery(pages.list(query));

  function body(): ReactElement {
    if (list.isPending) {
      return (
        <div {...stylex.props(screen.body)}>
          <Notice message="Chargement des pages…" />
        </div>
      );
    }
    if (list.isError) {
      return (
        <div {...stylex.props(screen.body)}>
          <Notice
            message="La liste des pages n'a pas pu être chargée"
            detail={list.error.message}
          />
        </div>
      );
    }
    return (
      <PagesScreen
        list={list.data}
        query={query}
        crawls={known.data ?? []}
        buckets={(stats.data?.buckets ?? []).map((bucket) => bucket.bucket)}
        hrefOf={(page) => `/pages/${page.id}?${params.toString()}`}
        onChange={(changes) => setParams(withChange(params, changes))}
        onReset={() => setParams(reset(params))}
        onSort={(field) => setParams(withSort(params, field))}
        onPage={(page) => setParams(withChange(params, { page: String(page) }))}
      />
    );
  }

  return (
    <>
      <TopBar crumbs={["SENTINEL", "PAGES"]}>
        <span {...stylex.props(styles.summary)}>
          {list.data === undefined
            ? "—"
            : `${count(list.data.total)} pages, ${count(list.data.flagged_total)} signalées`}
        </span>
      </TopBar>
      {body()}
    </>
  );
}
