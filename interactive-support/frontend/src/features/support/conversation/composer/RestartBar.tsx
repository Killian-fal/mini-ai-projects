import { Button } from "../../../../ui/Button";
import * as styles from "./RestartBar.css";

/** @package */
export function RestartBar({ onRestart }: { onRestart: () => void }) {
  return (
    <div className={styles.bar}>
      <Button variant="primary" size="large" onClick={onRestart}>
        Nouvelle demande
      </Button>
    </div>
  );
}
