import { useState } from "react";
import { cx } from "../../../../ui/cx";
import * as styles from "./ClampedText.css";

const CLAMP_AT = 600;

/** @package */
export function ClampedText({ text }: { text: string }) {
  const [open, setOpen] = useState(false);
  const long = text.length > CLAMP_AT;
  return (
    <>
      <p className={cx(styles.paragraph, long && !open && styles.clamped)}>{text}</p>
      {long && (
        <button
          type="button"
          aria-expanded={open}
          className={styles.toggle}
          onClick={() => setOpen(!open)}
        >
          {open ? "Réduire" : "Afficher tout"}
        </button>
      )}
    </>
  );
}
