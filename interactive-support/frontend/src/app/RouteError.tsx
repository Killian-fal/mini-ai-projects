import { useNavigate } from "@tanstack/react-router";
import { Button } from "../ui/Button";
import * as styles from "./RouteError.css";

export function RouteError() {
  const navigate = useNavigate();
  return (
    <main className={styles.error}>
      <p className={styles.eyebrow}>Erreur</p>
      <h1 className={styles.title}>Un problème est survenu.</h1>
      <p className={styles.lead}>
        La page n’a pas pu s’afficher. Vous pouvez décrire votre problème dans une nouvelle demande.
      </p>
      <Button variant="primary" size="large" onClick={() => void navigate({ to: "/" })}>
        Nouvelle demande
      </Button>
    </main>
  );
}
