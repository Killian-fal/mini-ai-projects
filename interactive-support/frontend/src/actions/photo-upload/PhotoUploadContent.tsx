import type { ReactNode } from "react";
import type { ActionOf } from "../../api/conversation";
import { Photo } from "../../ui/Photo";
import type { CardProps } from "../contract";
import { PhotoPicker } from "./PhotoPicker";
import * as styles from "./PhotoUploadContent.css";

const SENT_ALT = "Votre photo";

/** @package */
export function PhotoUploadContent({
  status,
  onAnswer,
}: CardProps<ActionOf<"PHOTO_UPLOAD">>): ReactNode {
  switch (status.state) {
    case "pending":
      return <PhotoPicker onAnswer={onAnswer} />;
    case "sending":
      return (
        <Photo src={status.response} alt={SENT_ALT} size="preview" className={styles.sending} />
      );
    case "answered":
    case "failed":
      return <Photo src={status.response} alt={SENT_ALT} size="thumb" />;
  }
}
