import * as stylex from "@stylexjs/stylex";
import { color, font, size } from "../../ui/tokens.stylex";

const ALL = "tous";

const styles = stylex.create({
  wrap: { display: "flex", alignItems: "center", gap: 10 },
  label: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.09em",
    textTransform: "uppercase",
    color: color.textDim,
  },
  field: { position: "relative", display: "flex", alignItems: "center" },
  select: {
    appearance: "none",
    fontFamily: font.data,
    fontSize: 11,
    letterSpacing: "0.04em",
    color: color.text,
    borderRadius: size.radius,
    padding: "5px 26px 5px 9px",
    cursor: "pointer",
    transitionDuration: size.motion,
    transitionProperty: "border-color, background",
    transitionTimingFunction: "ease",
    backgroundColor: { default: color.bgSurface, ":hover": color.bgRaised },
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: {
      default: color.line,
      ":hover": color.inert,
      ":focus-visible": color.inert,
    },
  },
  chevron: {
    position: "absolute",
    right: 9,
    fontSize: 9,
    color: color.textDim,
    pointerEvents: "none",
  },
});

export function CrawlSelect({
  value,
  options,
  onChange,
}: {
  value: string | null;
  options: string[];
  onChange: (crawl: string | null) => void;
}) {
  return (
    <div {...stylex.props(styles.wrap)}>
      <label htmlFor="crawl" {...stylex.props(styles.label)}>
        Crawl
      </label>
      <div {...stylex.props(styles.field)}>
        <select
          id="crawl"
          value={value ?? ALL}
          onChange={(event) =>
            onChange(event.target.value === ALL ? null : event.target.value)
          }
          {...stylex.props(styles.select)}
        >
          <option value={ALL}>{ALL}</option>
          {options.map((crawl) => (
            <option key={crawl} value={crawl}>
              {crawl}
            </option>
          ))}
        </select>
        <span aria-hidden="true" {...stylex.props(styles.chevron)}>
          ▾
        </span>
      </div>
    </div>
  );
}
