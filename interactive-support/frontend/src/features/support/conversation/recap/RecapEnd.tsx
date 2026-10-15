import { cx } from "../../../../ui/cx";
import type { Ending } from "../model";
import * as styles from "./RecapEnd.css";
import * as line from "./recapLine.css";

type RecapEndProps = {
  ending: Ending;
  onJump: (targets: readonly number[]) => void;
};

/** @package */
export function RecapEnd({ ending, onJump }: RecapEndProps) {
  return (
    <button
      type="button"
      className={cx(line.line, line.edge.strong, styles.end)}
      onClick={() => onJump(ending.targets)}
    >
      <span className={styles.label}>Fin de la conversation</span>
      <span className={styles.summary}>{ending.text}</span>
    </button>
  );
}
