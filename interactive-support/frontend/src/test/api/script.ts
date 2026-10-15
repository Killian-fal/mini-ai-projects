import type { ActionDto, ActionMessageDto, MessageDto } from "./dto";

export type Turn = { label: string | null; messages: MessageDto[] };

export type Step = (pending: ActionMessageDto, response: string) => Turn;

export const say = (code: string, text: string): MessageDto => ({ role: "ASSISTANT", code, text });

export const ask = (actionId: string, action: ActionDto): MessageDto => ({
  role: "ASSISTANT_ACTION",
  action_id: actionId,
  action,
});

export const finish = (text: string): MessageDto => ({
  role: "END",
  code: "OpeningCode.COMPLETE_CONVERSATION",
  text,
});

export const reask = (pending: ActionMessageDto, code: string, text: string): Turn => ({
  label: null,
  messages: [say(code, text), ask(pending.action_id, pending.action)],
});
