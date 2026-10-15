import type { ActionModule } from "../contract";
import { FormContent } from "./FormContent";
import { sentValues } from "./sentValues";

export const form: ActionModule<"FORM"> = {
  input: { kind: "card", prompt: "À compléter", width: "regular", Content: FormContent },
  answer: (action, response) => {
    const sent = sentValues(response);
    return {
      kind: "text",
      text:
        sent === null
          ? response
          : action.fields
              .map(({ key }) => sent[key])
              .filter(Boolean)
              .join(", "),
    };
  },
};
