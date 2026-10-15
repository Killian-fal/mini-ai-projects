import type { Action } from "../api/conversation";
import type { AnswerView } from "./contract";
import { moduleFor } from "./registry";

export function answerView(action: Action, response: string, label: string | null): AnswerView {
  return moduleFor(action).answer(action, response, label);
}
