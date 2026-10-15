import type { ActionModule } from "../contract";
import { yesNoLabel } from "./answers";
import { YesNoContent } from "./YesNoContent";

export const yesNo: ActionModule<"YES_NO"> = {
  input: { kind: "card", prompt: "À confirmer", width: "regular", Content: YesNoContent },
  answer: (_action, response) => ({ kind: "text", text: yesNoLabel(response) }),
};
