import * as stylex from "@stylexjs/stylex";
import type { ReactNode } from "react";
import { Link } from "react-router";
import { Badge } from "./Badge";
import { Gauge } from "./Gauge";
import { color, font, size } from "./tokens.stylex";

export type LineState = "normal" | "flagged" | "error";

const styles = stylex.create({
  row: {
    display: "grid",
    gap: "0 14px",
    alignItems: "center",
    borderBottomWidth: 1,
    borderBottomStyle: "solid",
    borderBottomColor: color.lineSoft,
    textDecoration: "none",
    color: "inherit",
    transitionDuration: size.motion,
    transitionProperty: "background",
    transitionTimingFunction: "ease",
    backgroundColor: { default: "transparent", ":hover": color.bgRowHover },
  },
  shape: (columns: string, pad: number) => ({
    gridTemplateColumns: columns,
    padding: `${pad}px 16px ${pad}px 13px`,
  }),
  rowFlagged: {
    backgroundColor: { default: color.bgSignalRow, ":hover": color.bgRowHoverSignal },
  },
  rail: { alignSelf: "stretch", borderRadius: size.radiusTight },
  railShape: (pad: number) => ({ margin: `${-pad}px 0` }),
  railFlagged: { backgroundColor: color.signal },
  railError: {
    backgroundImage: `repeating-linear-gradient(180deg, ${color.inert} 0 3px, transparent 3px 6px)`,
  },
  url: { minWidth: 0, display: "flex", flexDirection: "column", gap: 4 },
  line: {
    display: "flex",
    alignItems: "baseline",
    minWidth: 0,
    overflow: "hidden",
    whiteSpace: "nowrap",
    fontFamily: font.data,
    fontSize: 12,
  },
  host: { flex: "0 0 auto", fontWeight: 500, color: color.text },
  hostFlagged: { color: color.textStrong },
  hostError: { color: color.textMuted },
  path: {
    minWidth: 0,
    overflow: "hidden",
    textOverflow: "ellipsis",
    color: color.textMuted,
  },
  score: { display: "flex", alignItems: "center", gap: 9 },
  value: {
    fontFamily: font.data,
    fontSize: 12,
    width: 32,
    flexShrink: 0,
    textAlign: "right",
    color: color.textMuted,
  },
  valueFlagged: { color: color.signal },
  valueError: { color: color.textDim },
});

export function PageLine({
  to,
  columns,
  pad = 11,
  state,
  host,
  path,
  bucket,
  score,
  threshold,
  meta,
  children,
}: {
  to: string;
  columns: string;
  pad?: number;
  state: LineState;
  host: string;
  path: string;
  bucket: string;
  score: number | null;
  threshold: number | null;
  meta?: ReactNode;
  children?: ReactNode;
}) {
  const flagged = state === "flagged";
  const broken = state === "error";

  return (
    <Link
      to={to}
      {...stylex.props(
        styles.row,
        styles.shape(columns, pad),
        flagged && styles.rowFlagged,
      )}
    >
      <span
        {...stylex.props(
          styles.rail,
          styles.railShape(pad),
          broken && styles.railError,
          flagged && styles.railFlagged,
        )}
      />
      <span {...stylex.props(styles.url)}>
        <span {...stylex.props(styles.line)}>
          <span
            {...stylex.props(
              styles.host,
              broken && styles.hostError,
              flagged && styles.hostFlagged,
            )}
          >
            {host}
          </span>
          <span {...stylex.props(styles.path)}>{path}</span>
        </span>
        {meta}
      </span>
      <Badge label={bucket} />
      <span {...stylex.props(styles.score)}>
        <Gauge score={score} threshold={threshold} strong={flagged} broken={broken} />
        <span
          {...stylex.props(
            styles.value,
            broken && styles.valueError,
            flagged && styles.valueFlagged,
          )}
        >
          {score === null ? "n/a" : score.toFixed(2)}
        </span>
      </span>
      {children}
    </Link>
  );
}
