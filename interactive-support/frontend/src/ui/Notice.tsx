import type { ReactNode } from "react";
import { cx } from "./cx";
import * as styles from "./Notice.css";

type NoticeProps = {
  children: ReactNode;
  action?: ReactNode;
  className?: string;
};

export function Notice({ children, action, className }: NoticeProps) {
  return (
    <div role="status" className={cx(styles.notice, className)}>
      <span className={styles.icon} aria-hidden="true">
        !
      </span>
      <span className={styles.message}>{children}</span>
      {action}
    </div>
  );
}
