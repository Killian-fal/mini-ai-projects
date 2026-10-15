import type { ReactNode } from "react";
import type { AnswerView } from "../../../../actions";
import { cx } from "../../../../ui/cx";
import { Photo } from "../../../../ui/Photo";
import { Tag } from "../../../../ui/Tag";
import type { JournalRow } from "../model";
import * as styles from "./RecapRow.css";
import * as line from "./recapLine.css";

function answerView(answer: AnswerView | null): ReactNode {
  if (answer === null) {
    return <Tag tone="waiting">En attente</Tag>;
  }
  switch (answer.kind) {
    case "text":
      return <span className={styles.answer}>{answer.text}</span>;
    case "photo":
      return <Photo src={answer.src} alt="Votre photo" size="recap" />;
  }
}

type RecapRowProps = {
  number: number;
  row: JournalRow;
  onJump: (targets: readonly number[]) => void;
};

/** @package */
export function RecapRow({ number, row, onJump }: RecapRowProps) {
  return (
    <button
      type="button"
      className={cx(line.line, line.edge.soft, styles.row)}
      onClick={() => onJump(row.targets)}
    >
      <span className={styles.number}>{String(number).padStart(2, "0")}</span>
      <span className={styles.detail}>
        {row.question !== null && <span className={styles.question}>{row.question}</span>}
        {answerView(row.answer)}
      </span>
    </button>
  );
}
