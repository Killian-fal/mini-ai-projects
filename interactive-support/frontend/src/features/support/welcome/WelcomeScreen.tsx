import { cx } from "../../../ui/cx";
import { RelaisMark } from "../../../ui/RelaisMark";
import * as screen from "../screen.css";
import { WelcomeComposer } from "./WelcomeComposer";
import * as styles from "./WelcomeScreen.css";

type WelcomeScreenProps = {
  initialDraft: string;
  failed: boolean;
  onSend: (message: string) => void;
};

export function WelcomeScreen({ initialDraft, failed, onSend }: WelcomeScreenProps) {
  return (
    <main className={cx(screen.column, styles.welcome)}>
      <div className={styles.intro}>
        <p className={styles.identity}>
          <RelaisMark size="large" motion="still" />
          <span className={styles.name}>Relais</span>
          <span className={styles.role}>agent IA du Comptoir Ferrand</span>
        </p>
        <h1 className={styles.title}>Bonjour Camille, que pouvons-nous faire pour vous ?</h1>
        <p className={styles.lead}>
          Décrivez la situation avec vos mots. Je vous poserai ensuite quelques questions pour
          transmettre une demande complète au support.
        </p>
      </div>
      <WelcomeComposer initialDraft={initialDraft} failed={failed} onSend={onSend} />
    </main>
  );
}
