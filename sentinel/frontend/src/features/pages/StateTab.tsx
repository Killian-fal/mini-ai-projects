import type { StyleXStyles } from "@stylexjs/stylex";
import * as stylex from "@stylexjs/stylex";
import { useState } from "react";
import type { Detection } from "../../api/pages";
import { count } from "../../ui/format";
import { CHANNELS, chipOf, KEY_CHANNELS } from "../../ui/palette";
import { channelColor, color, font, size } from "../../ui/tokens.stylex";
import { Highlighted } from "./Highlighted";

const LINE = /^\[([a-z]+)\]\s?(.*)$/u;

const keyBorder: Record<string, StyleXStyles> = stylex.create({
  hidden: { borderColor: channelColor.hidden },
  comment: { borderColor: channelColor.comment },
});

const styles = stylex.create({
  block: { display: "flex", flexDirection: "column", gap: 14 },
  controls: {
    display: "flex",
    flexWrap: "wrap",
    alignItems: "center",
    gap: "8px 12px",
  },
  chips: { display: "flex", flexWrap: "wrap", gap: 5 },
  chip: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.05em",
    padding: "4px 7px",
    borderRadius: size.radius,
    borderWidth: 1,
    borderStyle: "solid",
    cursor: "pointer",
    backgroundColor: color.bgRaised,
    borderColor: color.inert,
    transitionDuration: size.motion,
    transitionProperty: "color, border-color, background",
    transitionTimingFunction: "ease",
  },
  chipKey: { backgroundColor: color.bgChannelKey },
  chipOff: {
    color: color.inertSoft,
    borderColor: color.line,
    backgroundColor: "transparent",
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
    whiteSpace: "nowrap",
  },
  banner: {
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: color.line,
    borderLeftWidth: 2,
    borderLeftColor: color.inert,
    borderRadius: size.radius,
    backgroundColor: color.bgSurface,
    padding: "8px 12px",
    fontFamily: font.data,
    fontSize: 11,
    letterSpacing: "0.04em",
    color: color.textMuted,
  },
  list: {
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: color.line,
    borderRadius: size.radius,
    backgroundColor: color.bgSurface,
    overflow: "hidden",
  },
  row: {
    display: "grid",
    gridTemplateColumns: "78px minmax(0, 1fr)",
    gap: 12,
    padding: "5px 14px",
    borderBottomWidth: 1,
    borderBottomStyle: "solid",
    borderBottomColor: color.bgRowHoverSignal,
    transitionDuration: size.motion,
    transitionProperty: "background",
    transitionTimingFunction: "ease",
    backgroundColor: { default: "transparent", ":hover": color.bgRowHover },
  },
  rowKey: {
    backgroundColor: { default: color.bgSignalRow, ":hover": color.bgRowHover },
  },
  channel: { fontFamily: font.data, fontSize: 11, letterSpacing: "0.04em" },
  text: {
    fontFamily: font.data,
    fontSize: 12,
    lineHeight: 1.7,
    wordBreak: "break-word",
    color: color.textMuted,
  },
  textKey: { color: color.text },
  empty: {
    padding: "32px 14px",
    textAlign: "center",
    fontSize: 13,
    color: color.textMuted,
  },
});

type Line = { channel: string; text: string };

/** The sent text groups its lines under a lone `[channel]` header; the full state prefixes
 * every line. A prefix sets the current channel, the bare lines that follow inherit it. */
function parse(state: string): Line[] {
  let channel = "visible";
  return state.split("\n").flatMap((raw) => {
    const found = LINE.exec(raw);
    if (found === null) {
      return [{ channel, text: raw }];
    }
    channel = found[1] ?? "visible";
    const text = found[2] ?? "";
    return text === "" ? [] : [{ channel, text }];
  });
}

export function StateTab({ detection }: { detection: Detection }) {
  const [off, setOff] = useState<string[]>([]);
  const [needle, setNeedle] = useState("");

  const { state, sent_chars, saved_chars, skipped_reason, truncated } = detection;
  const lines = parse(state);
  const shown = lines.filter(
    (line) =>
      !off.includes(line.channel) &&
      (needle === "" || line.text.toLowerCase().includes(needle.toLowerCase())),
  );

  return (
    <div {...stylex.props(styles.block)}>
      <div {...stylex.props(styles.controls)}>
        <div {...stylex.props(styles.chips)}>
          {CHANNELS.map((channel) => {
            const on = !off.includes(channel);
            return (
              <button
                key={channel}
                type="button"
                aria-pressed={on}
                onClick={() =>
                  setOff((current) =>
                    current.includes(channel)
                      ? current.filter((c) => c !== channel)
                      : [...current, channel],
                  )
                }
                {...stylex.props(
                  styles.chip,
                  KEY_CHANNELS.includes(channel) && styles.chipKey,
                  on ? chipOf(channel) : styles.chipOff,
                  on ? keyBorder[channel] : false,
                )}
              >
                {`[${channel}] ${lines.filter((l) => l.channel === channel).length}`}
              </button>
            );
          })}
        </div>
        <input
          type="text"
          aria-label="Chercher dans le state"
          placeholder="chercher dans le state…"
          value={needle}
          onChange={(event) => setNeedle(event.target.value)}
          {...stylex.props(styles.field)}
        />
        <span {...stylex.props(styles.countLabel)}>
          {needle === "" ? `${shown.length} lignes` : `${shown.length} lignes trouvées`}
        </span>
      </div>

      {sent_chars !== null && saved_chars !== null && (
        <span {...stylex.props(styles.countLabel)}>
          {`${count(sent_chars)} caractères envoyés, ${count(saved_chars)} retirés avant envoi`}
        </span>
      )}

      {skipped_reason !== null && (
        <div {...stylex.props(styles.banner)}>
          Aucun appel : tous les blocs déjà vus
        </div>
      )}

      {truncated && (
        <div {...stylex.props(styles.banner)}>Texte tronqué à 30 000 caractères</div>
      )}

      <div {...stylex.props(styles.list)}>
        {shown.map((line, index) => (
          <div
            // biome-ignore lint/suspicious/noArrayIndexKey: a state line's only identity is its position
            key={index}
            {...stylex.props(
              styles.row,
              KEY_CHANNELS.includes(line.channel) && styles.rowKey,
            )}
          >
            <span {...stylex.props(styles.channel, chipOf(line.channel))}>
              [{line.channel}]
            </span>
            <span
              {...stylex.props(
                styles.text,
                KEY_CHANNELS.includes(line.channel) && styles.textKey,
              )}
            >
              <Highlighted text={line.text} needle={needle} />
            </span>
          </div>
        ))}
        {shown.length === 0 && (
          <div {...stylex.props(styles.empty)}>Aucune ligne pour ces canaux</div>
        )}
      </div>
    </div>
  );
}
