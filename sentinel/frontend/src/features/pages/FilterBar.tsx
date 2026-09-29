import * as stylex from "@stylexjs/stylex";
import type { PageQuery } from "../../api/pages";
import { badgeOf } from "../../ui/palette";
import { color, font, size } from "../../ui/tokens.stylex";

const ALL = "tous";

const styles = stylex.create({
  bar: {
    display: "flex",
    flexWrap: "wrap",
    alignItems: "center",
    gap: "10px 14px",
    padding: "12px 14px",
    backgroundColor: color.bgSurface,
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: color.line,
    borderRadius: size.radius,
  },
  field: {
    flex: "1 1 180px",
    minWidth: 140,
    fontFamily: font.data,
    fontSize: 11,
    letterSpacing: "0.03em",
    color: color.text,
    backgroundColor: color.bgBase,
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: { default: color.line, ":focus-visible": color.inert },
    borderRadius: size.radius,
    padding: "6px 9px",
  },
  chips: { display: "flex", flexWrap: "wrap", alignItems: "center", gap: 5 },
  chip: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.06em",
    textTransform: "uppercase",
    padding: "4px 7px",
    borderRadius: size.radius,
    borderWidth: 1,
    borderStyle: "solid",
    cursor: "pointer",
    transitionDuration: size.motion,
    transitionProperty: "color, border-color, background",
    transitionTimingFunction: "ease",
  },
  chipOff: {
    color: color.textDim,
    borderColor: color.line,
    backgroundColor: "transparent",
  },
  select: {
    appearance: "none",
    fontFamily: font.data,
    fontSize: 11,
    color: color.text,
    backgroundColor: color.bgBase,
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: { default: color.line, ":hover": color.inert },
    borderRadius: size.radius,
    padding: "6px 24px 6px 9px",
    cursor: "pointer",
  },
  selectWrap: { position: "relative", display: "flex", alignItems: "center" },
  chevron: {
    position: "absolute",
    right: 8,
    fontSize: 9,
    color: color.textDim,
    pointerEvents: "none",
  },
  check: {
    display: "flex",
    alignItems: "center",
    gap: 6,
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.07em",
    textTransform: "uppercase",
    color: color.textDim,
    cursor: "pointer",
  },
  checkOnSignal: { color: color.signal },
  checkOn: { color: color.text },
  box: { width: 11, height: 11, cursor: "pointer", accentColor: color.signal },
  boxNeutral: { accentColor: color.textMuted },
  slider: { display: "flex", alignItems: "center", gap: 8 },
  label: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.07em",
    textTransform: "uppercase",
    color: color.textDim,
    whiteSpace: "nowrap",
  },
  range: { width: 84, cursor: "pointer", accentColor: color.text },
  value: { fontFamily: font.data, fontSize: 11, color: color.text, width: 30 },
  button: {
    marginLeft: "auto",
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    backgroundColor: "transparent",
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: { default: color.line, ":hover": color.inert },
    borderRadius: size.radius,
    padding: "5px 8px",
    cursor: "pointer",
    color: { default: color.textMuted, ":hover": color.text },
  },
});

export function FilterBar({
  query,
  crawls,
  buckets,
  onChange,
  onReset,
}: {
  query: PageQuery;
  crawls: string[];
  buckets: string[];
  onChange: (changes: Record<string, string | string[] | null>) => void;
  onReset: () => void;
}) {
  const chosen = query.bucket ?? [];
  const min = query.min_score ?? 0;

  return (
    <div {...stylex.props(styles.bar)}>
      <input
        type="text"
        aria-label="Filtrer sur l'url"
        placeholder="filtrer sur l'url…"
        value={query.q ?? ""}
        onChange={(event) => onChange({ q: event.target.value || null })}
        {...stylex.props(styles.field)}
      />

      <div {...stylex.props(styles.chips)}>
        {buckets.map((bucket) => {
          const on = chosen.includes(bucket);
          return (
            <button
              key={bucket}
              type="button"
              aria-pressed={on}
              onClick={() =>
                onChange({
                  bucket: on ? chosen.filter((b) => b !== bucket) : [...chosen, bucket],
                })
              }
              {...stylex.props(styles.chip, on ? badgeOf(bucket) : styles.chipOff)}
            >
              {bucket}
            </button>
          );
        })}
      </div>

      <div {...stylex.props(styles.selectWrap)}>
        <select
          aria-label="Crawl"
          value={query.crawl ?? ALL}
          onChange={(event) =>
            onChange({ crawl: event.target.value === ALL ? null : event.target.value })
          }
          {...stylex.props(styles.select)}
        >
          <option value={ALL}>{ALL}</option>
          {crawls.map((crawl) => (
            <option key={crawl} value={crawl}>
              {crawl}
            </option>
          ))}
        </select>
        <span aria-hidden="true" {...stylex.props(styles.chevron)}>
          ▾
        </span>
      </div>

      <label
        {...stylex.props(
          styles.check,
          query.flagged_only === true && styles.checkOnSignal,
        )}
      >
        <input
          type="checkbox"
          checked={query.flagged_only === true}
          onChange={(event) =>
            onChange({ flagged_only: event.target.checked ? "1" : null })
          }
          {...stylex.props(styles.box)}
        />
        Signalées
      </label>

      <label
        {...stylex.props(styles.check, query.with_error === true && styles.checkOn)}
      >
        <input
          type="checkbox"
          checked={query.with_error === true}
          onChange={(event) =>
            onChange({ with_error: event.target.checked ? "1" : null })
          }
          {...stylex.props(styles.box, styles.boxNeutral)}
        />
        Erreur
      </label>

      <div {...stylex.props(styles.slider)}>
        <label htmlFor="min-score" {...stylex.props(styles.label)}>
          Score min
        </label>
        <input
          id="min-score"
          type="range"
          min={0}
          max={0.99}
          step={0.01}
          value={min}
          onChange={(event) =>
            onChange({
              min_score: event.target.value === "0" ? null : event.target.value,
            })
          }
          {...stylex.props(styles.range)}
        />
        <span {...stylex.props(styles.value)}>{min.toFixed(2)}</span>
      </div>

      <button type="button" onClick={onReset} {...stylex.props(styles.button)}>
        Réinitialiser
      </button>
    </div>
  );
}
