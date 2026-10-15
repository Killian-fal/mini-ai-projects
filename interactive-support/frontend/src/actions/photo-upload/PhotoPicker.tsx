import { type ChangeEvent, type ReactNode, useRef } from "react";
import { DropZone } from "./DropZone";
import { PhotoError } from "./PhotoError";
import { PhotoPreview } from "./PhotoPreview";
import { ACCEPTED_TYPES } from "./photoRules";
import { type PhotoStage, usePhotoStage } from "./usePhotoStage";

type Handlers = {
  pick: () => void;
  take: (file: File) => void;
  send: (src: string) => void;
};

function stageView(stage: PhotoStage, { pick, take, send }: Handlers): ReactNode {
  switch (stage.kind) {
    case "empty":
      return <DropZone pickLabel="Choisir une photo" onPick={pick} onFile={take} />;
    case "rejected":
      return (
        <>
          <PhotoError problem={stage.problem} />
          <DropZone pickLabel="Choisir une autre photo" onPick={pick} onFile={take} />
        </>
      );
    case "preview":
      return <PhotoPreview src={stage.src} onSend={() => send(stage.src)} onReplace={pick} />;
  }
}

/** @package */
export function PhotoPicker({ onAnswer }: { onAnswer: (src: string) => void }) {
  const { stage, take } = usePhotoStage();
  const input = useRef<HTMLInputElement>(null);

  function handleChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.currentTarget.files?.[0];
    // Cleared so that picking the same file again still fires a change.
    event.currentTarget.value = "";
    if (file !== undefined) {
      take(file);
    }
  }

  return (
    <>
      <input
        ref={input}
        type="file"
        hidden={true}
        accept={ACCEPTED_TYPES.join(",")}
        onChange={handleChange}
      />
      {stageView(stage, { pick: () => input.current?.click(), take, send: onAnswer })}
    </>
  );
}
