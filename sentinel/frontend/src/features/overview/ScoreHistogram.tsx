import * as stylex from "@stylexjs/stylex";
import { useState } from "react";
import { plural } from "../../ui/format";
import { color, font, size } from "../../ui/tokens.stylex";

const BIN = 0.05;
const MIN_HEIGHT = 1.5;

const styles = stylex.create({
  frame: { position: "relative", paddingTop: 34 },
  // <fieldset> for its implicit `group` role; it only wraps the track,
  // because a fieldset as a flex container does not resolve its children's height.
  group: {
    margin: 0,
    padding: 0,
    minWidth: 0,
    borderWidth: 0,
    borderStyle: "none",
  },
  plot: {
    position: "relative",
    height: 176,
    display: "flex",
    alignItems: "flex-end",
    gap: 3,
  },
  base: {
    position: "absolute",
    left: 0,
    right: 0,
    bottom: 0,
    height: 1,
    backgroundColor: color.line,
  },
  mark: (left: string) => ({
    position: "absolute",
    top: -6,
    bottom: 0,
    left,
    width: 1,
    opacity: 0.85,
    backgroundColor: color.signal,
  }),
  column: {
    appearance: "none",
    borderWidth: 0,
    borderStyle: "none",
    backgroundColor: "transparent",
    padding: 0,
    fontFamily: "inherit",
    fontSize: "inherit",
    position: "relative",
    flex: 1,
    minWidth: 0,
    height: "100%",
    display: "flex",
    alignItems: "flex-end",
    cursor: "default",
  },
  bar: (height: string) => ({ height, width: "100%" }),
  shape: {
    borderTopLeftRadius: size.radiusTight,
    borderTopRightRadius: size.radiusTight,
    transitionDuration: size.motion,
    transitionProperty: "background, height",
    transitionTimingFunction: "ease",
  },
  under: { backgroundColor: { default: color.barNeutral, ":hover": color.inertSoft } },
  over: { backgroundColor: { default: color.signal, ":hover": color.signalHover } },
  tip: {
    position: "absolute",
    bottom: "100%",
    left: "50%",
    transform: "translate(-50%, -6px)",
    whiteSpace: "nowrap",
    zIndex: 2,
    padding: "4px 8px",
    backgroundColor: color.bgRaised,
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: color.inert,
    borderRadius: size.radius,
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.05em",
    color: color.text,
  },
  axis: {
    display: "flex",
    justifyContent: "space-between",
    paddingTop: 8,
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.06em",
    color: color.textDim,
  },
  axisMark: { color: color.signal },
});

export function ScoreHistogram({
  histogram,
  threshold,
  thresholdLabel,
}: {
  histogram: number[];
  threshold: number | null;
  thresholdLabel: string;
}) {
  const [hovered, setHovered] = useState(-1);
  const peak = Math.max(1, ...histogram);

  return (
    <div {...stylex.props(styles.frame)}>
      <fieldset
        aria-label={`Histogramme des scores, ${histogram.length} tranches`}
        {...stylex.props(styles.group)}
      >
        <div {...stylex.props(styles.plot)}>
          <div {...stylex.props(styles.base)} />
          {threshold !== null && (
            <div {...stylex.props(styles.mark(`${(threshold * 100).toFixed(0)}%`))} />
          )}
          {histogram.map((pages, index) => {
            const low = index * BIN;
            const over = threshold !== null && low + BIN > threshold;
            const label = `${low.toFixed(2)}–${(low + BIN).toFixed(2)} · ${plural(pages, "page")}`;
            return (
              <button
                // biome-ignore lint/suspicious/noArrayIndexKey: the bucket IS the index
                key={index}
                type="button"
                tabIndex={-1}
                aria-label={label}
                onMouseEnter={() => setHovered(index)}
                onMouseLeave={() => setHovered(-1)}
                onFocus={() => setHovered(index)}
                onBlur={() => setHovered(-1)}
                {...stylex.props(styles.column)}
              >
                <div
                  {...stylex.props(
                    styles.shape,
                    over ? styles.over : styles.under,
                    styles.bar(
                      `${Math.max(MIN_HEIGHT, (pages / peak) * 100).toFixed(1)}%`,
                    ),
                  )}
                />
                {hovered === index && (
                  <span {...stylex.props(styles.tip)}>{label}</span>
                )}
              </button>
            );
          })}
        </div>
      </fieldset>
      <div {...stylex.props(styles.axis)}>
        <span>0.00</span>
        <span>0.50</span>
        <span {...stylex.props(styles.axisMark)}>{`SEUIL ${thresholdLabel}`}</span>
        <span>1.00</span>
      </div>
    </div>
  );
}
