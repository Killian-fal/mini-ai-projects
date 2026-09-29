import * as stylex from "@stylexjs/stylex";
import { useQuery } from "@tanstack/react-query";
import type { ReactElement } from "react";
import { useSearchParams } from "react-router";
import { crawls } from "../../api/crawls";
import { overview } from "../../api/overview";
import { Notice } from "../../ui/Notice";
import { screen } from "../../ui/screen";
import { TopBar } from "../../ui/TopBar";
import { CrawlSelect } from "./CrawlSelect";
import { OverviewScreen } from "./OverviewScreen";

export function OverviewPage(): ReactElement {
  const [params, setParams] = useSearchParams();
  const crawl = params.get("crawl");
  const known = useQuery(crawls.list());
  const data = useQuery(overview.of(crawl));

  function body(): ReactElement {
    if (data.isPending) {
      return <Notice message="Chargement de la vue d'ensemble…" />;
    }
    if (data.isError) {
      return (
        <Notice
          message="La vue d'ensemble n'a pas pu être chargée"
          detail={data.error.message}
        />
      );
    }
    return <OverviewScreen overview={data.data} crawl={crawl} />;
  }

  return (
    <>
      <TopBar crumbs={["SENTINEL", "VUE D'ENSEMBLE"]}>
        <CrawlSelect
          value={crawl}
          options={known.data ?? []}
          onChange={(next) => setParams(next === null ? {} : { crawl: next })}
        />
      </TopBar>
      <div {...stylex.props(screen.body)}>{body()}</div>
    </>
  );
}
