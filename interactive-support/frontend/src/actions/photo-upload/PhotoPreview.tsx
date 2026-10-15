import { Button } from "../../ui/Button";
import { Photo } from "../../ui/Photo";
import * as styles from "./PhotoPreview.css";

type PhotoPreviewProps = {
  src: string;
  onSend: () => void;
  onReplace: () => void;
};

/** @package */
export function PhotoPreview({ src, onSend, onReplace }: PhotoPreviewProps) {
  return (
    <div className={styles.preview}>
      <Photo src={src} alt="Aperçu de votre photo" size="preview" />
      <div className={styles.actions}>
        <Button variant="primary" size="compact" onClick={onSend}>
          Envoyer la photo
        </Button>
        <Button variant="outline" size="compact" onClick={onReplace}>
          Changer de photo
        </Button>
      </div>
    </div>
  );
}
