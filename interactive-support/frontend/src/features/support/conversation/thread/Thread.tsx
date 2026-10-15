import { Fragment, type ReactNode } from "react";
import type { Language } from "../../../../api/conversation";
import { LabeledRule } from "../../../../ui/LabeledRule";
import type { ThreadItem } from "../model";
import { AgentMessage } from "./AgentMessage";
import { ClientMessage } from "./ClientMessage";
import { ErrorBubble } from "./ErrorBubble";
import * as styles from "./Thread.css";
import { ThreadCard } from "./ThreadCard";
import { ThreadEntry } from "./ThreadEntry";
import { UnsentMessage } from "./UnsentMessage";

type ThreadProps = {
  items: readonly ThreadItem[];
  language: Language | null;
  highlighted: readonly number[];
  onAnswer: (response: string) => void;
};

type Context = Omit<ThreadProps, "items">;

function itemView(item: ThreadItem, { language, highlighted, onAnswer }: Context): ReactNode {
  switch (item.kind) {
    case "client":
      return (
        <ThreadEntry anchor={item.anchor} highlighted={highlighted} entrance="message">
          <ClientMessage view={item.view} />
        </ThreadEntry>
      );
    case "unsent":
      return (
        <ThreadEntry anchor={null} highlighted={highlighted} entrance="message">
          <UnsentMessage view={item.view} />
        </ThreadEntry>
      );
    case "agent":
      return (
        <ThreadEntry anchor={item.anchor} highlighted={highlighted} entrance="message">
          <AgentMessage text={item.text} leads={item.leads} language={language} />
        </ThreadEntry>
      );
    case "card":
      return (
        <ThreadEntry anchor={item.anchor} highlighted={highlighted} entrance="own">
          <ThreadCard action={item.action} status={item.status} onAnswer={onAnswer} />
        </ThreadEntry>
      );
    case "error":
      return (
        <ThreadEntry anchor={null} highlighted={highlighted} entrance="message">
          <ErrorBubble />
        </ThreadEntry>
      );
    case "ended":
      return <LabeledRule>Conversation terminée</LabeledRule>;
  }
}

export function Thread({ items, ...context }: ThreadProps) {
  return (
    <div role="log" className={styles.thread}>
      {items.map((item) => (
        <Fragment key={item.key}>{itemView(item, context)}</Fragment>
      ))}
    </div>
  );
}
