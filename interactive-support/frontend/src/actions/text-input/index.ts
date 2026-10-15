import type { ActionModule } from "../contract";

export const textInput: ActionModule<"TEXT_INPUT"> = {
  input: { kind: "composer" },
  answer: (_action, response) => ({ kind: "text", text: response }),
};
