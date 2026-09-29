import * as stylex from "@stylexjs/stylex";
import type { Overview } from "../../api/overview";
import { count } from "../../ui/format";
import { color, font } from "../../ui/tokens.stylex";

const styles = stylex.create({
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: 24,
  },
  cell: {
    display: "flex",
    flexDirection: "column",
    gap: 8,
    paddingTop: 14,
    borderTopWidth: 1,
    borderTopStyle: "solid",
    borderTopColor: color.line,
  },
  value: {
    fontFamily: font.data,
    fontSize: 30,
    lineHeight: 1,
    letterSpacing: "-0.02em",
    color: color.text,
  },
  signal: { color: color.signal },
  label: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.09em",
    textTransform: "uppercase",
    color: color.textDim,
  },
  note: { fontSize: 12, color: color.textMuted },
});

export function Kpis({
  overview,
  thresholdLabel,
}: {
  overview: Overview;
  thresholdLabel: string;
}) {
  const share = overview.stored === 0 ? 0 : (100 * overview.analysed) / overview.stored;
  const megatokens = Math.round(overview.input_tokens / 1e6);

  const cells = [
    {
      value: count(overview.stored),
      label: "Pages stockées",
      note: "html compressé en base",
      signal: false,
    },
    {
      value: count(overview.analysed),
      label: "Pages analysées",
      note: `${share.toFixed(1)} % du corpus`,
      signal: false,
    },
    {
      value: count(overview.flagged),
      label: "Pages signalées",
      note: `score ≥ ${thresholdLabel}`,
      signal: true,
    },
    {
      value: `$${overview.cost_usd.toFixed(2)}`,
      label: "Coût cumulé",
      note: `${count(megatokens)} M tok. à 0,042 $/M`,
      signal: false,
    },
  ];

  return (
    <section {...stylex.props(styles.grid)}>
      {cells.map((cell) => (
        <div key={cell.label} {...stylex.props(styles.cell)}>
          <span {...stylex.props(styles.value, cell.signal && styles.signal)}>
            {cell.value}
          </span>
          <span {...stylex.props(styles.label)}>{cell.label}</span>
          <span {...stylex.props(styles.note)}>{cell.note}</span>
        </div>
      ))}
    </section>
  );
}
