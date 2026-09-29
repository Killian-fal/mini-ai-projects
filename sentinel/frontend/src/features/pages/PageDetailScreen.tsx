import * as stylex from "@stylexjs/stylex";
import type { ReactElement } from "react";
import { useState } from "react";
import type { PageDetail } from "../../api/pages";
import { Notice } from "../../ui/Notice";
import { color, font, size } from "../../ui/tokens.stylex";
import { AnswerPanel } from "./AnswerPanel";
import { DetailHeader } from "./DetailHeader";
import { HtmlTab } from "./HtmlTab";
import { type Neighbour, Neighbours } from "./Neighbours";
import { StateTab } from "./StateTab";

const NARROW = "(max-width: 1120px)";

const styles = stylex.create({
  grid: { display: "grid", alignItems: "start" },
  withPanel: {
    gridTemplateColumns: {
      default: `minmax(0, 1fr) ${size.aside}`,
      "@media (max-width: 1120px)": "minmax(0, 1fr)",
    },
  },
  alone: { gridTemplateColumns: "minmax(0, 1fr)" },
  main: {
    minWidth: 0,
    padding: {
      default: "24px 28px 72px",
      "@media (max-width: 640px)": "20px 20px 64px",
    },
    display: "flex",
    flexDirection: "column",
    gap: 24,
  },
  tabs: {
    display: "flex",
    alignItems: "center",
    borderBottomWidth: 1,
    borderBottomStyle: "solid",
    borderBottomColor: color.line,
  },
  tab: {
    fontFamily: font.data,
    fontSize: 11,
    letterSpacing: "0.07em",
    textTransform: "uppercase",
    backgroundColor: "transparent",
    borderWidth: 0,
    borderStyle: "none",
    borderBottomWidth: 2,
    borderBottomStyle: "solid",
    borderBottomColor: "transparent",
    padding: "9px 14px",
    marginBottom: -1,
    cursor: "pointer",
    color: { default: color.textDim, ":hover": color.text },
  },
  active: { color: color.text, borderBottomColor: color.signal },
  toggle: {
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
    padding: "4px 8px",
    cursor: "pointer",
    color: { default: color.textMuted, ":hover": color.text },
  },
});

export function PageDetailScreen({
  page,
  tab,
  onTab,
  html,
  htmlStatus,
  previous,
  next,
}: {
  page: PageDetail;
  tab: "state" | "html";
  onTab: (tab: "state" | "html") => void;
  html: string | undefined;
  htmlStatus: "pending" | "error" | "success";
  previous: Neighbour | null;
  next: Neighbour | null;
}) {
  const [panelOpen, setPanelOpen] = useState(() => !window.matchMedia(NARROW).matches);
  const [chosen, setChosen] = useState(0);

  const history = [...page.detections].reverse();
  const current = Math.min(chosen, history.length - 1);
  const detection = history[current];
  const broken = detection?.error != null;
  const withPanel = panelOpen && detection !== undefined;

  function analysis(): ReactElement {
    if (detection === undefined) {
      return (
        <Notice message="Cette page n'a pas encore été analysée" detail={page.crawl} />
      );
    }
    return (
      <>
        <div {...stylex.props(styles.tabs)}>
          <button
            type="button"
            onClick={() => onTab("state")}
            {...stylex.props(styles.tab, tab === "state" && styles.active)}
          >
            Ce que le modèle a vu
          </button>
          <button
            type="button"
            onClick={() => onTab("html")}
            {...stylex.props(styles.tab, tab === "html" && styles.active)}
          >
            HTML brut
          </button>
          <button
            type="button"
            onClick={() => setPanelOpen((open) => !open)}
            {...stylex.props(styles.toggle)}
          >
            {panelOpen ? "Masquer la réponse" : "Réponse du modèle"}
          </button>
        </div>
        {tab === "state" ? (
          <StateTab detection={detection} />
        ) : (
          <HtmlTab html={html} htmlBytes={page.html_bytes} status={htmlStatus} />
        )}
      </>
    );
  }

  return (
    <div {...stylex.props(styles.grid, withPanel ? styles.withPanel : styles.alone)}>
      <div {...stylex.props(styles.main)}>
        <DetailHeader
          page={page}
          score={broken ? null : (detection?.score ?? null)}
          threshold={detection?.threshold ?? null}
          broken={broken}
        />

        {analysis()}

        <Neighbours previous={previous} next={next} />
      </div>

      {withPanel && (
        <AnswerPanel
          detection={detection}
          history={history}
          current={current}
          onClose={() => setPanelOpen(false)}
          onSelect={setChosen}
        />
      )}
    </div>
  );
}
