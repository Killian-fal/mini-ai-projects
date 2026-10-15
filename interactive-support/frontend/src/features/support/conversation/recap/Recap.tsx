import { useId } from "react";
import type { Ending, JournalRow } from "../model";
import * as styles from "./Recap.css";
import { RecapEnd } from "./RecapEnd";
import { RecapRow } from "./RecapRow";

type RecapProps = {
  rows: readonly JournalRow[];
  ending: Ending | null;
  onJump: (targets: readonly number[]) => void;
};

export function Recap({ rows, ending, onJump }: RecapProps) {
  const titleId = useId();
  const empty = rows.length === 0 && ending === null;
  return (
    <section className={styles.recap} aria-labelledby={titleId}>
      <header className={styles.header}>
        <p className={styles.eyebrow}>Récap</p>
        <h2 id={titleId} className={styles.title}>
          Questions et réponses
        </h2>
      </header>
      {empty ? (
        <p className={styles.empty}>Les questions de l’agent et vos réponses s’afficheront ici.</p>
      ) : (
        <div className={styles.list}>
          {rows.map((row, index) => (
            <RecapRow key={row.actionId} number={index + 1} row={row} onJump={onJump} />
          ))}
          {ending !== null && <RecapEnd ending={ending} onJump={onJump} />}
        </div>
      )}
    </section>
  );
}
