import * as stylex from "@stylexjs/stylex";
import type { ReactElement } from "react";
import type { PageRow } from "../../api/overview";
import { bytes, pathOf, time } from "../../ui/format";
import { PageLine } from "../../ui/PageLine";
import { chipOf } from "../../ui/palette";
import { color, font, size } from "../../ui/tokens.stylex";

const styles = stylex.create({
  table: {
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: color.line,
    borderRadius: size.radius,
    overflow: "hidden",
  },
  head: {
    display: "grid",
    gridTemplateColumns: size.pagesGrid,
    gap: "0 14px",
    padding: "10px 16px 10px 13px",
    backgroundColor: color.bgSurface,
    borderBottomWidth: 1,
    borderBottomStyle: "solid",
    borderBottomColor: color.line,
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.09em",
    textTransform: "uppercase",
    color: color.textDim,
  },
  right: { textAlign: "right" },
  scroll: { overflowX: "auto" },
  min: { minWidth: 720 },
  meta: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    overflow: "hidden",
    whiteSpace: "nowrap",
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.06em",
    textTransform: "uppercase",
    color: color.textDim,
  },
  at: {
    fontFamily: font.data,
    fontSize: 11,
    color: color.textMuted,
    textAlign: "right",
  },
});

export function FlaggedPages({
  pages,
  threshold,
}: {
  pages: PageRow[];
  threshold: number | null;
}) {
  return (
    <div {...stylex.props(styles.scroll)}>
      <div {...stylex.props(styles.table, styles.min)}>
        <div {...stylex.props(styles.head)}>
          <span />
          <span>Page</span>
          <span>Bucket</span>
          <span>Score</span>
          <span {...stylex.props(styles.right)}>Analysée</span>
        </div>
        {pages.map((page) => (
          <PageLine
            key={page.id}
            to={`/pages/${page.id}`}
            columns={size.pagesGrid}
            pad={13}
            state={page.error == null ? (page.flagged ? "flagged" : "normal") : "error"}
            host={page.host ?? page.url}
            path={pathOf(page.url, page.host)}
            bucket={page.bucket}
            score={page.score ?? null}
            threshold={threshold}
            meta={meta(page)}
          >
            <span {...stylex.props(styles.at)}>
              {page.analysed_at == null ? "—" : time(page.analysed_at)}
            </span>
          </PageLine>
        ))}
      </div>
    </div>
  );
}

function meta(page: PageRow): ReactElement {
  return (
    <span {...stylex.props(styles.meta)}>
      <span>
        {page.crawl} · {bytes(page.html_bytes)}
      </span>
      {page.channels.map((channel) => (
        <span key={channel} {...stylex.props(chipOf(channel))}>
          [{channel}]
        </span>
      ))}
    </span>
  );
}
