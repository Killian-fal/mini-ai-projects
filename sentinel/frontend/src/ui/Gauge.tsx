import * as stylex from "@stylexjs/stylex";
import { color, size } from "./tokens.stylex";

const styles = stylex.create({
  // A track fills the available width, never more: `flex: 1` would also
  // stretch it vertically in a column container.
  track: {
    position: "relative",
    width: "100%",
    minWidth: 0,
    borderRadius: size.radius,
    backgroundColor: color.lineSoft,
  },
  broken: {
    backgroundImage: `repeating-linear-gradient(90deg, ${color.line} 0 3px, transparent 3px 6px)`,
  },
  height: (px: number) => ({ height: px }),
  // The gradient is stretched so the color follows the absolute score, not the width.
  fill: (score: number, floor: number) => ({
    width: `${(score * 100).toFixed(0)}%`,
    backgroundSize: `${(100 / Math.max(score, floor)).toFixed(0)}% 100%`,
    backgroundImage: color.gauge,
  }),
  fillShape: {
    position: "absolute",
    left: 0,
    top: 0,
    bottom: 0,
    borderRadius: size.radius,
  },
  tick: (left: string, overflow: number) => ({
    left,
    top: -overflow,
    bottom: -overflow,
  }),
  tickShape: { position: "absolute", width: 1 },
  tickStrong: { backgroundColor: color.text },
  tickIdle: { backgroundColor: color.inertSoft },
});

/** Track, fill and threshold mark. The numeric value is up to the caller. */
export function Gauge({
  score,
  threshold,
  strong = false,
  broken = false,
  height = 4,
  tickOverflow = 4,
}: {
  score: number | null;
  threshold?: number | null;
  strong?: boolean;
  broken?: boolean;
  height?: number;
  tickOverflow?: number;
}) {
  const floor = height > 4 ? 0.04 : 0.06;
  return (
    <span
      {...stylex.props(styles.track, styles.height(height), broken && styles.broken)}
    >
      {score !== null && (
        <span {...stylex.props(styles.fillShape, styles.fill(score, floor))} />
      )}
      {threshold !== null && threshold !== undefined && tickOverflow > 0 && (
        <span
          {...stylex.props(
            styles.tickShape,
            strong ? styles.tickStrong : styles.tickIdle,
            styles.tick(`${(threshold * 100).toFixed(0)}%`, tickOverflow),
          )}
        />
      )}
    </span>
  );
}
