import { useState } from "react";
import { checkPhoto, type PhotoProblem } from "./photoRules";
import { readDataUrl } from "./readDataUrl";

/** @package */
export type PhotoStage =
  | { kind: "empty" }
  | { kind: "rejected"; problem: PhotoProblem }
  | { kind: "preview"; src: string };

/** @package */
export function usePhotoStage() {
  const [stage, setStage] = useState<PhotoStage>({ kind: "empty" });

  function take(file: File) {
    const problem = checkPhoto(file);
    if (problem !== null) {
      setStage({ kind: "rejected", problem });
      return;
    }
    readDataUrl(file).then(
      (src) => setStage({ kind: "preview", src }),
      () => setStage({ kind: "rejected", problem: { kind: "not-an-image", name: file.name } }),
    );
  }

  return { stage, take };
}
