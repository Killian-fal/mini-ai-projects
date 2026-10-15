import type { Message } from "../../../../api/conversation";
import { isClient } from "./roles";

export function revealCount(messages: readonly Message[], shown: number): number {
  let visible = Math.min(shown, messages.length);
  while (isClient(messages[visible])) {
    visible += 1;
  }
  return visible;
}
