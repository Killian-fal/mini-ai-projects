import { Tag } from "../../ui/Tag";
import * as styles from "./PhotoError.css";
import { ACCEPTED_LABEL, formatMegabytes, MAX_MEGABYTES, type PhotoProblem } from "./photoRules";

type Explanation = { tag: string; message: string };

function explain(problem: PhotoProblem): Explanation {
  switch (problem.kind) {
    case "too-large":
      return {
        tag: "Photo trop lourde",
        message: `« ${problem.name} » pèse ${formatMegabytes(problem.bytes)}. Choisissez une image de moins de ${MAX_MEGABYTES} Mo.`,
      };
    case "not-an-image":
      return {
        tag: "Format non pris en charge",
        message: `« ${problem.name} » n’est pas une image. Choisissez un fichier ${ACCEPTED_LABEL}.`,
      };
  }
}

/** @package */
export function PhotoError({ problem }: { problem: PhotoProblem }) {
  const { tag, message } = explain(problem);
  return (
    <div role="status" className={styles.error}>
      <Tag tone="alert">{tag}</Tag>
      <p className={styles.message}>{message}</p>
    </div>
  );
}
