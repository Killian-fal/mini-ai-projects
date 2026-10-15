import { request } from "../http";
import type { Conversation } from "./types";

/** @package */
export function startConversation(message: string): Promise<Conversation> {
  return request("post", "/conversations", { body: { message } });
}

/** @package */
export function getConversation(conversationId: string): Promise<Conversation> {
  return request("get", "/conversations/{conversation_id}", {
    path: { conversation_id: conversationId },
  });
}

/** @package */
export function answer(
  conversationId: string,
  actionId: string,
  response: string,
): Promise<Conversation> {
  return request("post", "/conversations/{conversation_id}/answers", {
    path: { conversation_id: conversationId },
    body: { action_id: actionId, response },
  });
}
