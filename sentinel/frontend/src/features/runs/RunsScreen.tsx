import * as stylex from "@stylexjs/stylex";
import type { Daily, Run } from "../../api/runs";
import { plural } from "../../ui/format";
import { Notice } from "../../ui/Notice";
import { Section } from "../../ui/Section";
import { color, font } from "../../ui/tokens.stylex";
import { RunTable } from "./RunTable";
import { Sparkline } from "./Sparkline";

const styles = stylex.create({
  body: {
    display: "flex",
    flexDirection: "column",
    gap: 40,
    padding: {
      default: "32px 32px 80px",
      "@media (max-width: 640px)": "24px 20px 64px",
    },
  },
  sparks: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
    gap: 32,
  },
  mono: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    color: color.textDim,
  },
});

export function RunsScreen({ runs, daily }: { runs: Run[]; daily: Daily[] }) {
  return (
    <div {...stylex.props(styles.body)}>
      <section {...stylex.props(styles.sparks)}>
        <Sparkline
          label="Pages analysées par jour"
          values={daily.map((day) => day.analysed)}
          format={(value) => plural(value, "page")}
        />
        <Sparkline
          label="Taux de signalement"
          values={daily.map((day) => day.flagged_rate)}
          format={(value) => `${(value * 100).toFixed(2)} %`}
        />
      </section>

      <Section
        title="Runs"
        aside={<span {...stylex.props(styles.mono)}>Lancés en ligne de commande</span>}
      >
        {runs.length === 0 ? (
          <Notice
            message="Aucun run enregistré"
            detail="python -m sentinel.run --crawl CC-MAIN-2026-34 --threshold 0.80"
          />
        ) : (
          <RunTable runs={runs} />
        )}
      </Section>
    </div>
  );
}
