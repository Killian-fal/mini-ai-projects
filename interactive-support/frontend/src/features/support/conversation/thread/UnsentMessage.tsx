import type { AnswerView } from "../../../../actions";
import { ClientMessage } from "./ClientMessage";
import * as styles from "./UnsentMessage.css";

/** @package */
export function UnsentMessage({ view }: { view: AnswerView }) {
  return (
    <div className={styles.unsent}>
      <div className={styles.dimmed}>
        <ClientMessage view={view} />
      </div>
      <p className={styles.label}>Non envoyé</p>
    </div>
  );
}
