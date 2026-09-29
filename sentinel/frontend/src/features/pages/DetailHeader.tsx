import * as stylex from "@stylexjs/stylex";
import { useState } from "react";
import type { PageDetail } from "../../api/pages";
import { Badge } from "../../ui/Badge";
import { bytes, fullDate } from "../../ui/format";
import { Gauge } from "../../ui/Gauge";
import { bucketColor, color, font, size } from "../../ui/tokens.stylex";
import { RequestDialog } from "./RequestDialog";

const COPIED_MS = 1400;

const styles = stylex.create({
  head: {
    display: "flex",
    flexWrap: "wrap",
    gap: "20px 32px",
    justifyContent: "space-between",
    paddingBottom: 20,
    borderBottomWidth: 1,
    borderBottomStyle: "solid",
    borderBottomColor: color.line,
  },
  left: {
    minWidth: 0,
    display: "flex",
    flexDirection: "column",
    gap: 10,
    flex: "1 1 320px",
  },
  urlRow: { display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" },
  url: {
    fontFamily: font.data,
    fontSize: 13,
    lineHeight: 1.5,
    color: color.text,
    wordBreak: "break-all",
  },
  action: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    backgroundColor: "transparent",
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: { default: color.line, ":hover": color.inert },
    borderRadius: size.radius,
    padding: "3px 7px",
    cursor: "pointer",
    textDecoration: "none",
    color: { default: color.textMuted, ":hover": color.text },
  },
  facts: {
    display: "flex",
    alignItems: "center",
    gap: 12,
    flexWrap: "wrap",
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.07em",
    textTransform: "uppercase",
    color: color.textDim,
  },
  right: {
    flex: "0 1 300px",
    minWidth: 240,
    display: "flex",
    flexDirection: "column",
    gap: 10,
  },
  scoreRow: {
    display: "flex",
    alignItems: "flex-end",
    justifyContent: "space-between",
    gap: 12,
  },
  score: {
    fontFamily: font.data,
    fontSize: 40,
    lineHeight: 1,
    letterSpacing: "-0.02em",
  },
  scoreFlagged: { color: color.signal },
  scoreClean: { color: color.text },
  scoreBroken: { color: color.textDim },
  state: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.1em",
    textTransform: "uppercase",
    padding: "4px 8px",
    borderRadius: size.radius,
    borderWidth: 1,
    borderStyle: "solid",
  },
  flagged: {
    color: color.signal,
    borderColor: bucketColor.hiringLine,
    backgroundColor: bucketColor.hiringBg,
  },
  clean: {
    color: bucketColor.academicText,
    borderColor: bucketColor.academicLine,
    backgroundColor: bucketColor.academicBg,
  },
  idle: {
    color: color.textDim,
    borderColor: color.line,
    backgroundColor: color.bgRaised,
  },
  broken: {
    color: color.errorText,
    borderColor: color.inert,
    backgroundColor: color.bgRaised,
  },
  axis: {
    position: "relative",
    height: 12,
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.06em",
    color: color.textDim,
  },
  start: { position: "absolute", left: 0 },
  end: { position: "absolute", right: 0 },
  mark: (left: string) => ({ left }),
  markShape: {
    position: "absolute",
    transform: "translateX(-100%)",
    paddingRight: 6,
    whiteSpace: "nowrap",
    color: color.textMuted,
  },
});

type State = "broken" | "unanalysed" | "flagged" | "clean";

const LABEL: Record<State, string> = {
  broken: "Erreur",
  unanalysed: "Non analysée",
  flagged: "Signalée",
  clean: "Propre",
};
const SCORE_STYLE: Record<State, stylex.StyleXStyles> = {
  broken: styles.scoreBroken,
  unanalysed: styles.scoreBroken,
  flagged: styles.scoreFlagged,
  clean: styles.scoreClean,
};
const STATE_STYLE: Record<State, stylex.StyleXStyles> = {
  broken: styles.broken,
  unanalysed: styles.idle,
  flagged: styles.flagged,
  clean: styles.clean,
};

function stateOf(
  score: number | null,
  threshold: number | null,
  broken: boolean,
): State {
  if (broken) {
    return "broken";
  }
  if (score === null) {
    return "unanalysed";
  }
  return threshold !== null && score >= threshold ? "flagged" : "clean";
}

export function DetailHeader({
  page,
  score,
  threshold,
  broken,
}: {
  page: PageDetail;
  score: number | null;
  threshold: number | null;
  broken: boolean;
}) {
  const [copied, setCopied] = useState(false);
  const state = stateOf(score, threshold, broken);

  function copy(): void {
    void navigator.clipboard?.writeText(page.url);
    setCopied(true);
    setTimeout(() => setCopied(false), COPIED_MS);
  }

  return (
    <div {...stylex.props(styles.head)}>
      <div {...stylex.props(styles.left)}>
        <div {...stylex.props(styles.urlRow)}>
          <span {...stylex.props(styles.url)}>{page.url}</span>
          <button type="button" onClick={copy} {...stylex.props(styles.action)}>
            {copied ? "Copié" : "Copier"}
          </button>
          <a
            href={page.url}
            target="_blank"
            rel="noreferrer noopener"
            {...stylex.props(styles.action)}
          >
            Ouvrir ↗
          </a>
          <RequestDialog id={page.id} enabled={page.detections.length > 0} />
        </div>
        <div {...stylex.props(styles.facts)}>
          <Badge label={page.bucket} />
          <span>{page.crawl}</span>
          <span>Récupérée {fullDate(page.fetched_at)}</span>
          <span>{bytes(page.html_bytes)}</span>
        </div>
      </div>

      <div {...stylex.props(styles.right)}>
        <div {...stylex.props(styles.scoreRow)}>
          <span {...stylex.props(styles.score, SCORE_STYLE[state])}>
            {score === null ? "n/a" : score.toFixed(2)}
          </span>
          <span {...stylex.props(styles.state, STATE_STYLE[state])}>
            {LABEL[state]}
          </span>
        </div>
        {state !== "unanalysed" && (
          <>
            <Gauge
              score={score}
              threshold={threshold}
              strong
              broken={broken}
              height={6}
              tickOverflow={5}
            />
            <div {...stylex.props(styles.axis)}>
              <span {...stylex.props(styles.start)}>0.00</span>
              {threshold !== null && (
                <span
                  {...stylex.props(
                    styles.markShape,
                    styles.mark(`${(threshold * 100).toFixed(0)}%`),
                  )}
                >
                  {`SEUIL ${threshold.toFixed(2)}`}
                </span>
              )}
              <span {...stylex.props(styles.end)}>1.00</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
