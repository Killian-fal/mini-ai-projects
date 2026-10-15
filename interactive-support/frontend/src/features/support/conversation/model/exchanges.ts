import type { ActionMessage, Message, ResponseMessage } from "../../../../api/conversation";
import { questionText } from "./roles";

type At<T> = { index: number; message: T };

export type Exchange = {
  question: { index: number; text: string } | null;
  action: At<ActionMessage>;
  response: At<ResponseMessage> | null;
};

export function exchanges(messages: readonly Message[]): Exchange[] {
  const result: Exchange[] = [];
  messages.forEach((message, index) => {
    if (message.role === "ASSISTANT_ACTION") {
      const text = questionText(messages[index - 1]);
      result.push({
        question: text === null ? null : { index: index - 1, text },
        action: { index, message },
        response: null,
      });
    } else if (message.role === "USER_ACTION_RESPONSE") {
      const last = result.at(-1);
      if (last !== undefined && last.response === null) {
        last.response = { index, message };
      }
    }
  });
  return result;
}

export function pendingExchange(list: readonly Exchange[]): Exchange | null {
  const last = list.at(-1);
  return last !== undefined && last.response === null ? last : null;
}
