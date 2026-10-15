import type { ReactNode } from "react";
import { cx } from "../../../../ui/cx";
import { enterMessage } from "../../../../ui/theme/motion.css";
import { anchorId } from "../navigation/anchor";
import * as styles from "./ThreadEntry.css";

type ThreadEntryProps = {
  anchor: number | null;
  highlighted: readonly number[];
  entrance: "message" | "own";
  children: ReactNode;
};

/** @package */
export function ThreadEntry({ anchor, highlighted, entrance, children }: ThreadEntryProps) {
  return (
    <div
      id={anchor === null ? undefined : anchorId(anchor)}
      className={cx(
        styles.entry,
        entrance === "message" && enterMessage,
        anchor !== null && highlighted.includes(anchor) && styles.highlighted,
      )}
    >
      {children}
    </div>
  );
}
