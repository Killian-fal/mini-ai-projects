import { Notice } from "../../../../ui/Notice";
import * as styles from "./ErrorBubble.css";

/** @package */
export function ErrorBubble() {
  return (
    <div className={styles.row}>
      <Notice className={styles.bubble}>Un problème est survenu, vous pouvez réessayer.</Notice>
    </div>
  );
}
