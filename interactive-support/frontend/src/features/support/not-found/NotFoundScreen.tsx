import { Button } from "../../../ui/Button";
import { cx } from "../../../ui/cx";
import * as screen from "../screen.css";
import * as styles from "./NotFoundScreen.css";

export function NotFoundScreen({ onRestart }: { onRestart: () => void }) {
  return (
    <main className={cx(screen.column, styles.notFound)}>
      <p className={styles.eyebrow}>Conversation introuvable</p>
      <h1 className={styles.title}>Cette conversation n’existe plus.</h1>
      <p className={styles.lead}>
        Le lien ouvert ne correspond à aucune conversation en cours : elle a peut-être expiré ou été
        clôturée. Vous pouvez décrire votre problème dans une nouvelle demande.
      </p>
      <Button variant="primary" size="large" className={styles.action} onClick={onRestart}>
        Nouvelle demande
      </Button>
    </main>
  );
}
