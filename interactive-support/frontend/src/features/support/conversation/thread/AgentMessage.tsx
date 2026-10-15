import type { Language } from "../../../../api/conversation";
import { RelaisMark } from "../../../../ui/RelaisMark";
import * as styles from "./AgentMessage.css";

type AgentMessageProps = {
  text: string;
  leads: boolean;
  language: Language | null;
};

/** @package */
export function AgentMessage({ text, leads, language }: AgentMessageProps) {
  return (
    <div className={styles.agent}>
      {leads && (
        <p className={styles.signature}>
          <RelaisMark size="small" motion="still" />
          Relais
        </p>
      )}
      <div className={styles.body}>
        <p className={styles.paragraph} lang={language?.toLowerCase()}>
          {text}
        </p>
      </div>
    </div>
  );
}
