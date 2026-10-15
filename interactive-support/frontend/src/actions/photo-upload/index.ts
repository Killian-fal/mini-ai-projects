import type { ActionModule } from "../contract";
import { PhotoUploadContent } from "./PhotoUploadContent";

export const photoUpload: ActionModule<"PHOTO_UPLOAD"> = {
  input: { kind: "card", prompt: "Photo demandée", width: "narrow", Content: PhotoUploadContent },
  answer: (_action, response) => ({ kind: "photo", src: response }),
};
