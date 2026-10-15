import type { ReactNode } from "react";
import { ConversationScreen } from "./conversation/ConversationScreen";
import { NotFoundScreen } from "./not-found/NotFoundScreen";
import { SupportHeader } from "./SupportHeader";
import * as styles from "./SupportPage.css";
import { type SupportQuery, useSupport } from "./useSupport";
import { WelcomeScreen } from "./welcome/WelcomeScreen";

function body(query: SupportQuery): ReactNode {
  switch (query.screen) {
    case "welcome":
      return <WelcomeScreen initialDraft={query.draft} failed={query.failed} onSend={query.send} />;
    case "conversation":
      return (
        <ConversationScreen {...query.view} onAnswer={query.answer} onRestart={query.restart} />
      );
    case "not-found":
      return <NotFoundScreen onRestart={query.restart} />;
    case "loading":
      return null;
  }
}

export function SupportPage() {
  const query = useSupport();
  return (
    <div className={styles.shell}>
      <SupportHeader />
      {body(query)}
    </div>
  );
}
