import type { Message } from "../../../../api/conversation";

const CLIENT_ROLES: ReadonlySet<Message["role"]> = new Set(["USER", "USER_ACTION_RESPONSE"]);

export function isClient(message: Message | undefined): boolean {
  return message !== undefined && CLIENT_ROLES.has(message.role);
}

/** @package */
export function isAgent(message: Message | undefined): boolean {
  return message !== undefined && !CLIENT_ROLES.has(message.role);
}

/** @package */
export function questionText(message: Message | undefined): string | null {
  return message?.role === "ASSISTANT" || message?.role === "ASSISTANT_GEN" ? message.text : null;
}
