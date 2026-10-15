import type { Action, Message } from "../api/conversation";

export const user = (text: string): Message => ({ role: "USER", text });

export const agent = (text: string): Message => ({ role: "ASSISTANT", code: "TEST", text });

export const generated = (text: string): Message => ({ role: "ASSISTANT_GEN", text });

export const end = (text: string): Message => ({ role: "END", code: "TEST", text });

export const ask = (actionId: string, action: Action): Message => ({
  role: "ASSISTANT_ACTION",
  action_id: actionId,
  action,
});

export const reply = (
  actionId: string,
  response: string,
  label: string | null = null,
): Message => ({
  role: "USER_ACTION_RESPONSE",
  action_id: actionId,
  response,
  label,
});

export const textInput: Action = { type: "TEXT_INPUT" };

export const photoUpload: Action = { type: "PHOTO_UPLOAD" };

export const yesNo = (value: string): Action => ({ type: "YES_NO", value, location: null });

export const uniqueChoice = (...labels: string[]): Action => ({
  type: "UNIQUE_CHOICE",
  choices: labels.map((label, index) => ({ key: `CHOICE_${index}`, label })),
});

export const form = (...fields: [label: string, value: string][]): Action => ({
  type: "FORM",
  fields: fields.map(([label, value], index) => ({ key: `FIELD_${index}`, label, value })),
});
