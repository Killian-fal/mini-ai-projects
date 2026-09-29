import * as stylex from "@stylexjs/stylex";
import { useState } from "react";
import { bytes, plural } from "../../ui/format";
import { color, font, size } from "../../ui/tokens.stylex";
import { Highlighted } from "./Highlighted";

const styles = stylex.create({
  block: { display: "flex", flexDirection: "column", gap: 14 },
  controls: { display: "flex", flexWrap: "wrap", alignItems: "center", gap: 10 },
  button: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    backgroundColor: "transparent",
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: { default: color.line, ":hover": color.inert },
    borderRadius: size.radius,
    padding: "5px 9px",
    cursor: "pointer",
    color: { default: color.textMuted, ":hover": color.text },
  },
  field: {
    flex: "1 1 160px",
    minWidth: 130,
    fontFamily: font.data,
    fontSize: 11,
    color: color.text,
    backgroundColor: color.bgBase,
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: { default: color.line, ":focus-visible": color.inert },
    borderRadius: size.radius,
    padding: "5px 9px",
  },
  countLabel: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.07em",
    textTransform: "uppercase",
    color: color.textDim,
  },
  code: {
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: color.line,
    borderRadius: size.radius,
    backgroundColor: color.bgSurface,
    padding: "10px 0",
    maxHeight: 520,
    overflow: "auto",
  },
  row: {
    display: "grid",
    gridTemplateColumns: "52px minmax(0, 1fr)",
    gap: 10,
    padding: "1px 14px 1px 0",
  },
  rowHit: { backgroundColor: color.bgRowHoverSignal },
  number: {
    fontFamily: font.data,
    fontSize: 11,
    color: color.inert,
    textAlign: "right",
    userSelect: "none",
  },
  text: {
    fontFamily: font.data,
    fontSize: 11.5,
    lineHeight: 1.65,
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
    color: color.textMuted,
  },
});

export function HtmlTab({
  html,
  htmlBytes,
  status,
}: {
  html: string | undefined;
  htmlBytes: number;
  status: "pending" | "error" | "success";
}) {
  const [open, setOpen] = useState(true);
  const [needle, setNeedle] = useState("");

  const lines = html === undefined ? [] : html.split("\n");
  const shown =
    needle === ""
      ? lines.map((text, index) => ({ text, number: index + 1, hit: false }))
      : lines
          .map((text, index) => ({
            text,
            number: index + 1,
            hit: text.toLowerCase().includes(needle.toLowerCase()),
          }))
          .filter((line) => line.hit);

  return (
    <div {...stylex.props(styles.block)}>
      <div {...stylex.props(styles.controls)}>
        <button
          type="button"
          onClick={() => setOpen((current) => !current)}
          {...stylex.props(styles.button)}
        >
          {open ? "Replier" : "Déplier"}
        </button>
        <input
          type="text"
          aria-label="Chercher dans le html"
          placeholder="chercher dans le html…"
          value={needle}
          onChange={(event) => setNeedle(event.target.value)}
          {...stylex.props(styles.field)}
        />
        <span {...stylex.props(styles.countLabel)}>
          {status === "pending"
            ? "Chargement…"
            : status === "error"
              ? "HTML indisponible"
              : needle === ""
                ? `${plural(shown.length, "ligne")} · ${bytes(htmlBytes)} en base`
                : plural(shown.length, "ligne")}
        </span>
      </div>

      {open && shown.length > 0 && (
        <div {...stylex.props(styles.code)}>
          {shown.map((line) => (
            <div
              key={line.number}
              {...stylex.props(styles.row, line.hit && styles.rowHit)}
            >
              <span {...stylex.props(styles.number)}>{line.number}</span>
              <span {...stylex.props(styles.text)}>
                <Highlighted text={line.text} needle={needle} />
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
