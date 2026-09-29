import * as stylex from "@stylexjs/stylex";
import type { Detection } from "../../api/pages";
import { count, dayTime } from "../../ui/format";
import { Gauge } from "../../ui/Gauge";
import { color, font, jsonColor, size } from "../../ui/tokens.stylex";
import { jsonTokens } from "./highlight";

const styles = stylex.create({
  aside: {
    padding: "24px 20px 48px",
    display: "flex",
    flexDirection: "column",
    gap: 22,
    minWidth: 0,
    borderLeftWidth: { default: 1, "@media (max-width: 1120px)": 0 },
    borderLeftStyle: "solid",
    borderLeftColor: color.line,
    borderTopWidth: { default: 0, "@media (max-width: 1120px)": 1 },
    borderTopStyle: "solid",
    borderTopColor: color.line,
    position: { default: "sticky", "@media (max-width: 1120px)": "static" },
    top: size.asideTop,
  },
  head: {
    display: "flex",
    alignItems: "baseline",
    justifyContent: "space-between",
    gap: 12,
  },
  title: { margin: 0, fontSize: 13, fontWeight: 500 },
  close: {
    fontFamily: font.data,
    fontSize: 11,
    backgroundColor: "transparent",
    borderWidth: 0,
    borderStyle: "none",
    padding: 0,
    cursor: "pointer",
    color: { default: color.textDim, ":hover": color.text },
  },
  json: {
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: color.line,
    borderRadius: size.radius,
    backgroundColor: color.bgSurface,
    padding: 12,
    overflowX: "auto",
  },
  pre: {
    margin: 0,
    fontFamily: font.data,
    fontSize: 11,
    lineHeight: 1.7,
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
  },
  key: { color: jsonColor.key },
  string: { color: jsonColor.string },
  number: { color: jsonColor.number },
  literal: { color: jsonColor.literal },
  punctuation: { color: jsonColor.punctuation },
  rows: { display: "flex", flexDirection: "column", gap: 8 },
  row: {
    display: "flex",
    justifyContent: "space-between",
    gap: 12,
    paddingBottom: 6,
    borderBottomWidth: 1,
    borderBottomStyle: "solid",
    borderBottomColor: color.lineSoft,
  },
  label: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    color: color.textDim,
  },
  value: {
    fontFamily: font.data,
    fontSize: 11,
    textAlign: "right",
    color: color.textMuted,
  },
  first: { color: color.text },
  history: {
    display: "grid",
    gridTemplateColumns: "34px minmax(0, 1fr) auto",
    gap: 10,
    alignItems: "center",
    textAlign: "left",
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: { default: color.line, ":hover": color.inert },
    borderRadius: size.radius,
    padding: "7px 9px",
    cursor: "pointer",
    backgroundColor: "transparent",
  },
  current: { backgroundColor: color.bgRaised, borderColor: color.inert },
  score: { fontFamily: font.data, fontSize: 12, color: color.textMuted },
  scoreFlagged: { color: color.signal },
  at: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.05em",
    color: color.textDim,
    whiteSpace: "nowrap",
  },
});

const TOKEN = {
  key: styles.key,
  string: styles.string,
  number: styles.number,
  literal: styles.literal,
  punctuation: styles.punctuation,
};

export function AnswerPanel({
  detection,
  history,
  current,
  onClose,
  onSelect,
}: {
  detection: Detection;
  history: Detection[];
  current: number;
  onClose: () => void;
  onSelect: (index: number) => void;
}) {
  const facts: [string, string][] = [
    ["Modèle", detection.model],
    ["Tokens entrée", count(detection.usage?.input_tokens ?? 0)],
    ["Tokens sortie", count(detection.usage?.output_tokens ?? 0)],
    [
      "Latence",
      detection.latency_ms == null ? "—" : `${count(detection.latency_ms)} ms`,
    ],
    ["Seuil", detection.threshold.toFixed(2)],
    ["Analysée", dayTime(detection.at)],
  ];

  return (
    <aside {...stylex.props(styles.aside)}>
      <div {...stylex.props(styles.head)}>
        <h2 {...stylex.props(styles.title)}>Réponse du modèle</h2>
        <button
          type="button"
          aria-label="Masquer la réponse du modèle"
          onClick={onClose}
          {...stylex.props(styles.close)}
        >
          ✕
        </button>
      </div>

      <div {...stylex.props(styles.json)}>
        <pre {...stylex.props(styles.pre)}>
          {jsonTokens(detection.answers).map((token, index) => (
            // biome-ignore lint/suspicious/noArrayIndexKey: a token's only identity is its position
            <span key={index} {...stylex.props(TOKEN[token.kind])}>
              {token.text}
            </span>
          ))}
        </pre>
      </div>

      <div {...stylex.props(styles.rows)}>
        {facts.map(([label, value], index) => (
          <div key={label} {...stylex.props(styles.row)}>
            <span {...stylex.props(styles.label)}>{label}</span>
            <span {...stylex.props(styles.value, index === 0 && styles.first)}>
              {value}
            </span>
          </div>
        ))}
      </div>

      <div {...stylex.props(styles.rows)}>
        <span {...stylex.props(styles.label)}>Détections précédentes</span>
        {history.map((one, index) => (
          <button
            key={one.at}
            type="button"
            aria-current={index === current}
            onClick={() => onSelect(index)}
            {...stylex.props(styles.history, index === current && styles.current)}
          >
            <span {...stylex.props(styles.score, one.flagged && styles.scoreFlagged)}>
              {one.score === null ? "n/a" : one.score.toFixed(2)}
            </span>
            <Gauge score={one.score} height={3} tickOverflow={0} />
            <span {...stylex.props(styles.at)}>{dayTime(one.at)}</span>
          </button>
        ))}
      </div>
    </aside>
  );
}
