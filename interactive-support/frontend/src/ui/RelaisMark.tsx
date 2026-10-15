import { cx } from "./cx";
import * as styles from "./RelaisMark.css";

type RelaisMarkProps = {
  size: keyof typeof styles.size;
  motion: "still" | "swapping";
};

export function RelaisMark({ size, motion }: RelaisMarkProps) {
  const swapping = motion === "swapping";
  return (
    <span className={cx(styles.mark, styles.size[size])} aria-hidden="true">
      <span className={cx(styles.team, swapping && styles.teamSwapping)} />
      <span className={cx(styles.agent, swapping && styles.agentSwapping)} />
    </span>
  );
}
