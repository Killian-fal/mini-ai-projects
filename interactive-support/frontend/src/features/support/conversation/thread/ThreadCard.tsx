import { ActionCard, type CardStatus } from "../../../../actions";
import type { Action } from "../../../../api/conversation";
import * as styles from "./ThreadCard.css";

type ThreadCardProps = {
  action: Action;
  status: CardStatus;
  onAnswer: (response: string) => void;
};

/** @package */
export function ThreadCard({ action, status, onAnswer }: ThreadCardProps) {
  return (
    <div className={styles.card}>
      <ActionCard action={action} status={status} onAnswer={onAnswer} />
    </div>
  );
}
