import * as styles from "./SupportHeader.css";

/** @package */
export function SupportHeader() {
  return (
    <header className={styles.header}>
      <p className={styles.brand}>
        <span className={styles.shop}>Comptoir Ferrand</span>
        <span className={styles.section}>Support</span>
      </p>
      <p className={styles.customer}>
        <span className={styles.name}>Camille Martin</span>
        <span className={styles.avatar} aria-hidden="true">
          CM
        </span>
      </p>
    </header>
  );
}
