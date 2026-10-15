import { RelaisMark } from "../../../../ui/RelaisMark";
import * as styles from "./Thinking.css";

const SECOND_CAPTION_MS = 3000;
const THIRD_CAPTION_MS = 6000;

function caption(elapsed: number): string {
  if (elapsed < SECOND_CAPTION_MS) {
    return "Relais réfléchit";
  }
  return elapsed < THIRD_CAPTION_MS ? "Prépare sa réponse" : "Encore un instant";
}

export function Thinking({ elapsed }: { elapsed: number | null }) {
  const label = elapsed === null ? null : caption(elapsed);
  return (
    <div className={styles.thinking}>
      <RelaisMark size="small" motion="swapping" />
      {label !== null && (
        <span key={label} className={styles.caption}>
          {label}
        </span>
      )}
    </div>
  );
}
