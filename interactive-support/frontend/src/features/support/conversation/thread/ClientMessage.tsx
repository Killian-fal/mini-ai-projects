import type { ReactNode } from "react";
import type { AnswerView } from "../../../../actions";
import { Photo } from "../../../../ui/Photo";
import { ClampedText } from "./ClampedText";
import * as styles from "./ClientMessage.css";

function content(view: AnswerView): ReactNode {
  switch (view.kind) {
    case "text":
      return (
        <div className={styles.bubble}>
          <ClampedText text={view.text} />
        </div>
      );
    case "photo":
      return <Photo src={view.src} alt="Photo envoyée" size="reply" />;
  }
}

/** @package */
export function ClientMessage({ view }: { view: AnswerView }) {
  return <div className={styles.row}>{content(view)}</div>;
}
