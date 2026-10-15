import type { Message } from "../../../../api/conversation";
import { questionText } from "./roles";

export type Ending = { text: string; targets: number[] };

export function ending(messages: readonly Message[]): Ending | null {
  const last = messages.at(-1);
  if (last?.role !== "END") {
    return null;
  }
  const texts = [last.text];
  for (let index = messages.length - 2; index >= 0; index -= 1) {
    const text = questionText(messages[index]);
    if (text === null) {
      break;
    }
    texts.unshift(text);
  }
  return { text: texts.join(" "), targets: [messages.length - 1] };
}
