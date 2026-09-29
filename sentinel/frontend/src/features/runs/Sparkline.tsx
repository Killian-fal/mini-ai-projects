import * as stylex from "@stylexjs/stylex";
import { useState } from "react";
import { color, font, size } from "../../ui/tokens.stylex";

const HEIGHT = 52;
const MIN_BAR = 2;

const styles = stylex.create({
  block: {
    display: "flex",
    flexDirection: "column",
    gap: 12,
    paddingTop: 14,
    borderTopWidth: 1,
    borderTopStyle: "solid",
    borderTopColor: color.line,
  },
  head: { display: "flex", flexDirection: "column", gap: 4, minWidth: 0 },
  label: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.09em",
    textTransform: "uppercase",
    color: color.textDim,
  },
  readout: {
    fontFamily: font.data,
    fontSize: 14,
    whiteSpace: "nowrap",
    overflow: "hidden",
    textOverflow: "ellipsis",
    color: color.text,
  },
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
    height: HEIGHT,
    display: "flex",
    alignItems: "flex-end",
    gap: 2,
  },
  column: {
    appearance: "none",
    borderWidth: 0,
    borderStyle: "none",
    backgroundColor: "transparent",
    padding: 0,
    flex: 1,
    minWidth: 0,
    height: "100%",
    display: "flex",
    alignItems: "flex-end",
    cursor: "default",
  },
  bar: (height: string) => ({ height }),
  barShape: {
    width: "100%",
    borderTopLeftRadius: size.radiusTight,
    borderTopRightRadius: size.radiusTight,
    backgroundColor: color.barNeutral,
    transitionDuration: size.motion,
    transitionProperty: "background",
    transitionTimingFunction: "ease",
  },
  hovered: { backgroundColor: color.text },
  axis: {
    display: "flex",
    justifyContent: "space-between",
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.06em",
    color: color.textDim,
  },
});

export function Sparkline({
  label,
  values,
  format,
}: {
  label: string;
  values: number[];
  format: (value: number) => string;
}) {
  const [hovered, setHovered] = useState(-1);
  const peak = Math.max(1, ...values);
  const shown = hovered >= 0 ? values[hovered] : values.at(-1);

  return (
    <div {...stylex.props(styles.block)}>
      <div {...stylex.props(styles.head)}>
        <span {...stylex.props(styles.label)}>{label}</span>
        <span {...stylex.props(styles.readout)}>
          {shown === undefined
            ? "—"
            : `${format(shown)} · ${hovered >= 0 ? `J-${values.length - 1 - hovered}` : "aujourd'hui"}`}
        </span>
      </div>
      <fieldset
        aria-label={`${label}, ${values.length} jours`}
        {...stylex.props(styles.group)}
      >
        <div {...stylex.props(styles.plot)}>
          {values.map((value, index) => (
            <button
              // biome-ignore lint/suspicious/noArrayIndexKey: the day IS the position
              key={index}
              type="button"
              tabIndex={-1}
              aria-label={`J-${values.length - 1 - index} · ${format(value)}`}
              onMouseEnter={() => setHovered(index)}
              onMouseLeave={() => setHovered(-1)}
              onFocus={() => setHovered(index)}
              onBlur={() => setHovered(-1)}
              {...stylex.props(styles.column)}
            >
              <span
                {...stylex.props(
                  styles.barShape,
                  hovered === index && styles.hovered,
                  styles.bar(`${Math.max(MIN_BAR, (value / peak) * 100).toFixed(1)}%`),
                )}
              />
            </button>
          ))}
        </div>
      </fieldset>
      <div {...stylex.props(styles.axis)}>
        <span>J-{Math.max(0, values.length - 1)}</span>
        <span>J-0</span>
      </div>
    </div>
  );
}
