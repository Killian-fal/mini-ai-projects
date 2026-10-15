import { type DragEvent, useState } from "react";
import { Button } from "../../ui/Button";
import { cx } from "../../ui/cx";
import * as styles from "./DropZone.css";
import { ACCEPTED_LABEL, MAX_MEGABYTES } from "./photoRules";

type DropZoneProps = {
  pickLabel: string;
  onPick: () => void;
  onFile: (file: File) => void;
};

/** @package */
export function DropZone({ pickLabel, onPick, onFile }: DropZoneProps) {
  const [dragging, setDragging] = useState(false);

  function handleDragOver(event: DragEvent) {
    event.preventDefault();
    setDragging(true);
  }

  function handleDragLeave(event: DragEvent) {
    const { relatedTarget, currentTarget } = event;
    if (!(relatedTarget instanceof Node && currentTarget.contains(relatedTarget))) {
      setDragging(false);
    }
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault();
    setDragging(false);
    const file = event.dataTransfer.files[0];
    if (file !== undefined) {
      onFile(file);
    }
  }

  return (
    <fieldset
      aria-label="Dépôt de la photo"
      className={cx(styles.zone, dragging && styles.dragging)}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <p className={styles.invite}>Glissez une photo ici, ou</p>
      <Button variant="primary" size="compact" onClick={onPick}>
        {pickLabel}
      </Button>
      <p className={styles.formats}>
        {ACCEPTED_LABEL} · {MAX_MEGABYTES} Mo maximum
      </p>
    </fieldset>
  );
}
