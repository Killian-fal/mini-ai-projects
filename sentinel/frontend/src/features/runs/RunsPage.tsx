import * as stylex from "@stylexjs/stylex";
import { useQuery } from "@tanstack/react-query";
import type { ReactElement } from "react";
import { runs } from "../../api/runs";
import { plural } from "../../ui/format";
import { Notice } from "../../ui/Notice";
import { screen } from "../../ui/screen";
import { TopBar } from "../../ui/TopBar";
import { color, font } from "../../ui/tokens.stylex";
import { RunsScreen } from "./RunsScreen";

const styles = stylex.create({
  summary: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.09em",
    textTransform: "uppercase",
    color: color.textDim,
  },
});

export function RunsPage(): ReactElement {
  const all = useQuery(runs.list());

  function body(): ReactElement {
    if (all.isPending) {
      return (
        <div {...stylex.props(screen.body)}>
          <Notice message="Chargement des runs…" />
        </div>
      );
    }
    if (all.isError) {
      return (
        <div {...stylex.props(screen.body)}>
          <Notice
            message="Les runs n'ont pas pu être chargés"
            detail={all.error.message}
          />
        </div>
      );
    }
    return <RunsScreen runs={all.data.runs} daily={all.data.daily} />;
  }

  return (
    <>
      <TopBar crumbs={["SENTINEL", "RUNS"]}>
        <span {...stylex.props(styles.summary)}>{summary(all.data?.runs)}</span>
      </TopBar>
      {body()}
    </>
  );
}

function summary(
  list: { analysed: number; flagged: number; cost_usd: number }[] | undefined,
): string {
  if (list === undefined) {
    return "—";
  }
  if (list.length === 0) {
    return "aucun run";
  }
  const pages = list.reduce((total, run) => total + run.analysed, 0);
  const flagged = list.reduce((total, run) => total + run.flagged, 0);
  const cost = list.reduce((total, run) => total + run.cost_usd, 0);
  return `${plural(list.length, "run")} · ${plural(pages, "page")} · ${plural(flagged, "signalée")} · $${cost.toFixed(2)}`;
}
