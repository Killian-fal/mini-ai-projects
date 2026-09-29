import * as stylex from "@stylexjs/stylex";
import { Link } from "react-router";
import type { Overview } from "../../api/overview";
import { plural } from "../../ui/format";
import { Notice } from "../../ui/Notice";
import { Section } from "../../ui/Section";
import { color, font } from "../../ui/tokens.stylex";
import { BucketBars } from "./BucketBars";
import { FlaggedPages } from "./FlaggedPages";
import { Kpis } from "./Kpis";
import { ScoreHistogram } from "./ScoreHistogram";

const styles = stylex.create({
  columns: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(380px, 1fr))",
    gap: 40,
  },
  mono: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    color: color.textDim,
  },
  signal: { color: color.signal },
  link: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.09em",
    textTransform: "uppercase",
    textDecoration: "none",
    color: { default: color.textMuted, ":hover": color.text },
  },
});

export function OverviewScreen({
  overview,
  crawl,
}: {
  overview: Overview;
  crawl: string | null;
}) {
  const threshold = overview.threshold;
  const thresholdLabel = threshold === null ? "—" : threshold.toFixed(2);
  const crawlLabel = crawl ?? "tous les crawls";
  const search = crawl === null ? "" : `?crawl=${encodeURIComponent(crawl)}`;

  return (
    <>
      <Kpis overview={overview} thresholdLabel={thresholdLabel} />

      <div {...stylex.props(styles.columns)}>
        <Section
          title="Distribution des scores"
          aside={<span {...stylex.props(styles.mono)}>20 × 0.05</span>}
        >
          <ScoreHistogram
            histogram={overview.histogram}
            threshold={threshold}
            thresholdLabel={thresholdLabel}
          />
        </Section>

        <Section
          title="Répartition par bucket"
          aside={
            <span {...stylex.props(styles.mono)}>
              Pages · <span {...stylex.props(styles.signal)}>signalées</span>
            </span>
          }
        >
          <BucketBars buckets={overview.buckets} />
        </Section>
      </div>

      <Section
        title="Dernières pages signalées"
        aside={
          <Link to={`/pages${search}`} {...stylex.props(styles.link)}>
            Toutes les pages →
          </Link>
        }
      >
        {overview.latest_flagged.length === 0 ? (
          <Notice
            message={`Aucune injection détectée sur ${plural(overview.analysed, "page")}`}
            detail={`${crawlLabel} · seuil ${thresholdLabel}`}
          />
        ) : (
          <FlaggedPages pages={overview.latest_flagged} threshold={threshold} />
        )}
      </Section>
    </>
  );
}
