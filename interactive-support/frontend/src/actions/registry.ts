import type { Action, ActionType } from "../api/conversation";
import type { ActionModule, ActionRegistry } from "./contract";
import { form } from "./form";
import { photoUpload } from "./photo-upload";
import { textInput } from "./text-input";
import { uniqueChoice } from "./unique-choice";
import { yesNo } from "./yes-no";

const ACTIONS = {
  UNIQUE_CHOICE: uniqueChoice,
  YES_NO: yesNo,
  PHOTO_UPLOAD: photoUpload,
  TEXT_INPUT: textInput,
  FORM: form,
} satisfies ActionRegistry;

/** @package */
export function moduleFor(action: Action): ActionModule<ActionType> {
  // TS cannot correlate ACTIONS[action.type] with action: the registry guarantees it.
  return ACTIONS[action.type] as ActionModule<ActionType>;
}
