import type { ReactNode } from "react";
import { cx } from "./cx";
import * as styles from "./Tag.css";

type TagProps = {
  tone: keyof typeof styles.tone;
  children: ReactNode;
};

export function Tag({ tone, children }: TagProps) {
  return <span className={cx(styles.base, styles.tone[tone])}>{children}</span>;
}
