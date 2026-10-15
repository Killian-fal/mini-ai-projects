import { ApiError } from "../http";

export function isConversationNotFound(error: unknown): boolean {
  return error instanceof ApiError && error.code === "CONVERSATION_NOT_FOUND";
}

export function isActionNotFound(error: unknown): boolean {
  return error instanceof ApiError && error.code.startsWith("ACTION_NOT_FOUND");
}
