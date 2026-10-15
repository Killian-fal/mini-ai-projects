import type { Language, Message } from "../../../api/conversation";
import * as styles from "./ConversationScreen.css";
import { Composer } from "./composer/Composer";
import { composerState } from "./composer/composerState";
import {
  type Delivery,
  ending,
  exchanges,
  journalRows,
  pendingExchange,
  type SentAnswer,
  threadItems,
} from "./model";
import { useFollowBottom } from "./navigation/useFollowBottom";
import { useHighlight } from "./navigation/useHighlight";
import { Recap } from "./recap/Recap";
import { useElapsed } from "./reveal/useElapsed";
import { useReveal } from "./reveal/useReveal";
import { Thinking } from "./thinking/Thinking";
import { Thread } from "./thread/Thread";

const ACK_MS = 500;

type ConversationScreenProps = {
  messages: readonly Message[];
  language: Language | null;
  waiting: boolean;
  outgoing: SentAnswer | null;
  failure: SentAnswer | null;
  onAnswer: (answer: SentAnswer) => void;
  onRestart: () => void;
};

export function ConversationScreen({
  messages,
  language,
  waiting,
  outgoing,
  failure,
  onAnswer,
  onRestart,
}: ConversationScreenProps) {
  const visible = useReveal(messages);
  const elapsed = useElapsed(waiting);
  const { highlighted, jump } = useHighlight();

  const shown = messages.slice(0, visible);
  const delivery: Delivery = { outgoing, acked: elapsed >= ACK_MS, failure };
  const revealing = visible < messages.length;
  const thinking = (waiting && (outgoing === null || delivery.acked)) || revealing;
  const pending = pendingExchange(exchanges(shown));
  const items = threadItems(shown, delivery);

  useFollowBottom(`${items.at(-1)?.key ?? ""}:${thinking}`);

  function answerPending(response: string) {
    if (pending !== null) {
      onAnswer({ actionId: pending.action.message.action_id, response });
    }
  }

  return (
    <div className={styles.layout}>
      <aside className={styles.aside}>
        <Recap rows={journalRows(shown)} ending={ending(shown)} onJump={jump} />
      </aside>
      <main className={styles.main}>
        <div className={styles.flow}>
          <Thread
            items={items}
            language={language}
            highlighted={highlighted}
            onAnswer={answerPending}
          />
          {thinking && (
            <Thinking elapsed={waiting ? elapsed - (outgoing === null ? 0 : ACK_MS) : null} />
          )}
        </div>
        <div className={styles.composer}>
          <Composer
            state={composerState({
              ended: shown.at(-1)?.role === "END",
              busy: waiting || revealing,
              pending,
              delivery,
            })}
            onSend={answerPending}
            onRestart={onRestart}
          />
        </div>
      </main>
    </div>
  );
}
