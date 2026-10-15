import type { ActionModule } from "../contract";
import { UniqueChoiceContent } from "./UniqueChoiceContent";

export const uniqueChoice: ActionModule<"UNIQUE_CHOICE"> = {
  input: {
    kind: "card",
    prompt: "Choisissez une réponse",
    width: "regular",
    Content: UniqueChoiceContent,
  },
  answer: (action, response, label) => ({
    kind: "text",
    text: label ?? action.choices.find((choice) => choice.key === response)?.label ?? response,
  }),
};
