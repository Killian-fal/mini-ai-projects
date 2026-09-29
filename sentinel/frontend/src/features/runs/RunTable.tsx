import * as stylex from "@stylexjs/stylex";
import { Link } from "react-router";
import type { Run } from "../../api/runs";
import { count, dayTime } from "../../ui/format";
import { color, font, size } from "../../ui/tokens.stylex";

const styles = stylex.create({
  scroll: {
    overflowX: "auto",
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: color.line,
    borderRadius: size.radius,
  },
  min: { minWidth: 1040 },
  head: {
    display: "grid",
    gridTemplateColumns: size.runsGrid,
    gap: "0 12px",
    padding: "9px 16px 9px 13px",
    backgroundColor: color.bgSurface,
    borderBottomWidth: 1,
    borderBottomStyle: "solid",
    borderBottomColor: color.line,
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    color: color.textDim,
  },
  row: {
    display: "grid",
    gridTemplateColumns: size.runsGrid,
    gap: "0 12px",
    padding: "12px 16px 12px 13px",
    alignItems: "center",
    borderBottomWidth: 1,
    borderBottomStyle: "solid",
    borderBottomColor: color.lineSoft,
    fontFamily: font.data,
    fontSize: 12,
    textDecoration: "none",
    color: "inherit",
    transitionDuration: size.motion,
    transitionProperty: "background",
    transitionTimingFunction: "ease",
    backgroundColor: { default: "transparent", ":hover": color.bgRowHover },
  },
  rail: { alignSelf: "stretch", margin: "-12px 0", borderRadius: size.radiusTight },
  railOn: { backgroundColor: color.signal },
  right: { textAlign: "right" },
  strong: { color: color.text },
  muted: { color: color.textMuted },
  dim: { color: color.textDim },
  model: { color: color.textMuted, fontSize: 11 },
  signal: { color: color.signal },
  error: { color: color.errorText },
});

const HEADERS = [
  "Début",
  "Modèle",
  "Seuil",
  "Analysées",
  "Signalées",
  "Erreurs",
  "Tokens",
  "Coût",
  "Durée",
  "Lat. méd.",
];

export function RunTable({ runs }: { runs: Run[] }) {
  return (
    <div {...stylex.props(styles.scroll)}>
      <div {...stylex.props(styles.min)}>
        <div {...stylex.props(styles.head)}>
          <span />
          {HEADERS.map((header, index) => (
            <span key={header} {...stylex.props(index >= 3 && styles.right)}>
              {header}
            </span>
          ))}
        </div>
        {runs.map((run) => (
          <Link
            key={run.id}
            to={`/pages?run=${encodeURIComponent(run.id)}`}
            {...stylex.props(styles.row)}
          >
            <span {...stylex.props(styles.rail, run.flagged > 0 && styles.railOn)} />
            <span {...stylex.props(styles.strong)}>{dayTime(run.started_at)}</span>
            <span {...stylex.props(styles.model)}>{run.model}</span>
            <span {...stylex.props(styles.muted)}>{run.threshold.toFixed(2)}</span>
            <span {...stylex.props(styles.strong, styles.right)}>
              {count(run.analysed)}
            </span>
            <span
              {...stylex.props(
                styles.right,
                run.flagged > 0 ? styles.signal : styles.dim,
              )}
            >
              {count(run.flagged)}
            </span>
            <span
              {...stylex.props(
                styles.right,
                run.errors > 0 ? styles.error : styles.dim,
              )}
            >
              {count(run.errors)}
            </span>
            <span {...stylex.props(styles.muted, styles.right)}>
              {`${(run.input_tokens / 1e6).toFixed(1)}/${(run.output_tokens / 1e6).toFixed(2)} M`}
            </span>
            <span {...stylex.props(styles.muted, styles.right)}>
              {`$${run.cost_usd.toFixed(2)}`}
            </span>
            <span {...stylex.props(styles.muted, styles.right)}>
              {duration(run.duration_ms)}
            </span>
            <span {...stylex.props(styles.dim, styles.right)}>
              {run.median_latency_ms === null
                ? "—"
                : `${count(Math.round(run.median_latency_ms))} ms`}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}

function duration(ms: number): string {
  const minutes = Math.floor(ms / 60_000);
  const hours = Math.floor(minutes / 60);
  return hours > 0
    ? `${hours} h ${String(minutes % 60).padStart(2, "0")}`
    : `${minutes} min`;
}
