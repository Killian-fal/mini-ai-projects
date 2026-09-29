import * as stylex from "@stylexjs/stylex";
import type { ReactElement } from "react";
import type { PageQuery, PageRow, SortField } from "../../api/pages";
import { bytes, count, dayTime, midTrunc, pathOf } from "../../ui/format";
import { PageLine } from "../../ui/PageLine";
import { color, font, size } from "../../ui/tokens.stylex";

const PATH_MAX = 42;

const styles = stylex.create({
  scroll: {
    overflowX: "auto",
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: color.line,
    borderRadius: size.radius,
  },
  min: { minWidth: 980 },
  head: {
    display: "grid",
    gridTemplateColumns: size.listGrid,
    gap: "0 14px",
    padding: "9px 16px 9px 13px",
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
  sort: {
    font: "inherit",
    letterSpacing: "inherit",
    textTransform: "inherit",
    backgroundColor: "transparent",
    borderWidth: 0,
    borderStyle: "none",
    padding: 0,
    textAlign: "left",
    cursor: "pointer",
    color: { default: color.textDim, ":hover": color.text },
    transitionDuration: size.motion,
    transitionProperty: "color",
    transitionTimingFunction: "ease",
  },
  sortActive: { color: color.text },
  right: { textAlign: "right" },
  cell: { fontFamily: font.data, fontSize: 11, color: color.textDim },
  empty: {
    padding: "48px 20px",
    textAlign: "center",
    fontSize: 14,
    color: color.textMuted,
  },
});

const COLUMNS: { field: SortField; label: string; right: boolean }[] = [
  { field: "score", label: "Score", right: false },
  { field: "html_bytes", label: "Taille", right: false },
  { field: "analysed_at", label: "Analysée", right: true },
];

export function PageTable({
  rows,
  query,
  hrefOf,
  onSort,
}: {
  rows: PageRow[];
  query: PageQuery;
  hrefOf: (page: PageRow) => string;
  onSort: (field: SortField) => void;
}) {
  function header(field: SortField): ReactElement {
    const column = COLUMNS.find((c) => c.field === field);
    const active = query.sort === field;
    return (
      <button
        type="button"
        onClick={() => onSort(field)}
        {...stylex.props(
          styles.sort,
          active && styles.sortActive,
          column?.right === true && styles.right,
        )}
      >
        {column?.label} {active ? (query.order === "asc" ? "▴" : "▾") : ""}
      </button>
    );
  }

  return (
    <div {...stylex.props(styles.scroll)}>
      <div {...stylex.props(styles.min)}>
        <div {...stylex.props(styles.head)}>
          <span />
          <span>URL</span>
          <span>Bucket</span>
          {header("score")}
          <span>Tokens</span>
          {header("html_bytes")}
          {header("analysed_at")}
        </div>

        {rows.map((page) => (
          <PageLine
            key={page.id}
            to={hrefOf(page)}
            columns={size.listGrid}
            state={page.error == null ? (page.flagged ? "flagged" : "normal") : "error"}
            host={page.host ?? page.url}
            path={midTrunc(pathOf(page.url, page.host), PATH_MAX)}
            bucket={page.bucket}
            score={page.score ?? null}
            threshold={page.threshold ?? null}
          >
            <span {...stylex.props(styles.cell)}>
              {page.input_tokens == null
                ? "—"
                : `${count(page.input_tokens)}/${page.output_tokens ?? 0}`}
            </span>
            <span {...stylex.props(styles.cell)}>{bytes(page.html_bytes)}</span>
            <span {...stylex.props(styles.cell, styles.right)}>
              {page.analysed_at == null ? "—" : dayTime(page.analysed_at)}
            </span>
          </PageLine>
        ))}

        {rows.length === 0 && (
          <div {...stylex.props(styles.empty)}>
            Aucune page ne correspond à ces filtres
          </div>
        )}
      </div>
    </div>
  );
}
