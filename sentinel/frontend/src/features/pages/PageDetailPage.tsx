import * as stylex from "@stylexjs/stylex";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import type { ReactElement } from "react";
import { useState } from "react";
import { Link, useParams, useSearchParams } from "react-router";
import type { PageRow } from "../../api/pages";
import { pages } from "../../api/pages";
import { count, midTrunc, pathOf } from "../../ui/format";
import { Notice } from "../../ui/Notice";
import { screen } from "../../ui/screen";
import { TopBar } from "../../ui/TopBar";
import { color, font } from "../../ui/tokens.stylex";
import { SIZE, SORT_LABEL, toQuery } from "./filters";
import type { Neighbour } from "./Neighbours";
import { PageDetailScreen } from "./PageDetailScreen";

const NEIGHBOUR_MAX = 22;

const styles = stylex.create({
  summary: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.09em",
    textTransform: "uppercase",
    color: color.textDim,
    whiteSpace: "nowrap",
  },
  crumb: {
    textDecoration: "none",
    color: { default: color.textMuted, ":hover": color.text },
  },
  last: { color: color.text, overflow: "hidden", textOverflow: "ellipsis" },
});

export function PageDetailPage(): ReactElement {
  const { id = "" } = useParams();
  const [params] = useSearchParams();
  const [tab, setTab] = useState<"state" | "html">("state");

  const query = toQuery(params);
  const detail = useQuery(pages.detail(id));
  const html = useQuery({ ...pages.html(id), enabled: tab === "html" });

  const cached = useQueryClient().getQueryData(pages.list(query).queryKey);
  const items = cached?.items ?? [];
  const at = items.findIndex((row) => row.id === id);
  const position = at === -1 ? null : ((query.page ?? 1) - 1) * SIZE + at + 1;

  const search = params.toString();
  const link = (row: PageRow | undefined): Neighbour | null =>
    row === undefined
      ? null
      : {
          to: `/pages/${row.id}${search === "" ? "" : `?${search}`}`,
          label: `${row.host ?? row.url}${midTrunc(pathOf(row.url, row.host), NEIGHBOUR_MAX)}`,
        };

  function body(): ReactElement {
    if (detail.isPending) {
      return (
        <div {...stylex.props(screen.body)}>
          <Notice message="Chargement de la page…" />
        </div>
      );
    }
    if (detail.isError) {
      return (
        <div {...stylex.props(screen.body)}>
          <Notice message="Cette page est introuvable" detail={detail.error.message} />
        </div>
      );
    }
    return (
      <PageDetailScreen
        page={detail.data}
        tab={tab}
        onTab={setTab}
        html={html.data}
        htmlStatus={tab === "html" ? html.status : "pending"}
        previous={at <= 0 ? null : link(items[at - 1])}
        next={at === -1 ? null : link(items[at + 1])}
      />
    );
  }

  return (
    <>
      <TopBar
        crumbs={[
          "SENTINEL",
          <Link
            key="pages"
            to={{ pathname: "/pages", search }}
            {...stylex.props(styles.crumb)}
          >
            PAGES
          </Link>,
          <span key="host" {...stylex.props(styles.last)}>
            {(detail.data?.host ?? "").toUpperCase()}
          </span>,
        ]}
      >
        <span {...stylex.props(styles.summary)}>
          {position === null || cached === undefined
            ? `Tri ${SORT_LABEL[query.sort ?? "score"]}`
            : `Page ${position} / ${count(cached.total)} · tri ${SORT_LABEL[query.sort ?? "score"]}`}
        </span>
      </TopBar>
      {body()}
    </>
  );
}
