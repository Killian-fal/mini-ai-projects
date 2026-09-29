import * as stylex from "@stylexjs/stylex";
import type { BucketCount } from "../../api/overview";
import { count } from "../../ui/format";
import { color, font, size } from "../../ui/tokens.stylex";

const styles = stylex.create({
  list: { display: "flex", flexDirection: "column", gap: 14 },
  row: {
    display: "grid",
    gridTemplateColumns: "92px minmax(0, 1fr) 92px",
    gap: 12,
    alignItems: "center",
  },
  name: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.06em",
    textTransform: "uppercase",
    color: color.textMuted,
    overflow: "hidden",
    textOverflow: "ellipsis",
  },
  track: { position: "relative", height: 10, backgroundColor: color.bgRaised },
  fill: (width: string) => ({ width }),
  layer: {
    position: "absolute",
    left: 0,
    top: 0,
    bottom: 0,
    transitionDuration: size.motion,
    transitionProperty: "width",
    transitionTimingFunction: "ease",
  },
  total: { backgroundColor: color.barNeutral },
  flagged: { backgroundColor: color.signal },
  numbers: {
    fontFamily: font.data,
    fontSize: 11,
    color: color.textMuted,
    textAlign: "right",
  },
  signal: { color: color.signal },
});

export function BucketBars({ buckets }: { buckets: BucketCount[] }) {
  const peak = Math.max(1, ...buckets.map((bucket) => bucket.count));
  // categories come from the database: a new one shows up without touching the front
  const rows = [...buckets].sort((a, b) => b.count - a.count);

  return (
    <div {...stylex.props(styles.list)}>
      {rows.map(({ bucket: name, count: total, flagged }) => (
        <div key={name} {...stylex.props(styles.row)}>
          <span {...stylex.props(styles.name)}>{name}</span>
          <div {...stylex.props(styles.track)}>
            <div
              {...stylex.props(
                styles.layer,
                styles.total,
                styles.fill(`${((total / peak) * 100).toFixed(1)}%`),
              )}
            />
            <div
              {...stylex.props(
                styles.layer,
                styles.flagged,
                styles.fill(
                  flagged === 0
                    ? "0px"
                    : `max(2px, ${((flagged / peak) * 100).toFixed(3)}%)`,
                ),
              )}
            />
          </div>
          <span {...stylex.props(styles.numbers)}>
            {count(total)}{" "}
            {flagged > 0 && <span {...stylex.props(styles.signal)}>· {flagged}</span>}
          </span>
        </div>
      ))}
    </div>
  );
}
