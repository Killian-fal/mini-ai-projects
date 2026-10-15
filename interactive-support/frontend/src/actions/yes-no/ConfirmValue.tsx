import { cx } from "../../ui/cx";
import * as styles from "./ConfirmValue.css";

const SHORT_MAX = 60;

type ConfirmValueProps = {
  value: string;
  locked: boolean;
};

/** @package */
export function ConfirmValue({ value, locked }: ConfirmValueProps) {
  const short = value.length <= SHORT_MAX && !value.includes("\n");
  return (
    <p
      className={cx(
        styles.value,
        styles.length[short ? "short" : "long"],
        styles.tone[locked ? "locked" : "open"],
      )}
    >
      {value}
    </p>
  );
}
