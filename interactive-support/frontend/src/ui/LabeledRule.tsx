import * as styles from "./LabeledRule.css";

export function LabeledRule({ children }: { children: string }) {
  return <p className={styles.rule}>{children}</p>;
}
