import { HttpResponse, http } from "msw/http";
import { CANCEL_STEPS } from "./cancelFlow";
import { DAMAGED_STEPS, opening } from "./damagedFlow";
import type { ActionMessageDto, ConversationDto, MessageDto } from "./dto";
import type { Step } from "./script";

export const API_URL = "http://localhost:5002";

const MAX_MESSAGE = 2000;
const MAX_RESPONSE = 10_000_000;

const conversations = new Map<string, ConversationDto>();
let created = 0;

const STEPS: Record<string, Step> = { ...DAMAGED_STEPS, ...CANCEL_STEPS };

const notFound = () => HttpResponse.json({ detail: "CONVERSATION_NOT_FOUND" }, { status: 404 });

const invalid = (field: string) =>
  HttpResponse.json(
    { detail: [{ loc: ["body", field], msg: "Invalid", type: "value_error" }] },
    { status: 422 },
  );

function text(body: unknown, field: string, max: number): string | null {
  if (typeof body !== "object" || body === null || !(field in body)) {
    return null;
  }
  const value: unknown = Reflect.get(body, field);
  return typeof value === "string" && value.length <= max ? value : null;
}

export function resetConversations() {
  conversations.clear();
}

export function startedConversation(): ConversationDto {
  const [conversation] = conversations.values();
  if (conversation === undefined) {
    throw new Error("No conversation was started");
  }
  return conversation;
}

export function seedConversation(message: string, responses: readonly string[]): ConversationDto {
  let conversation: ConversationDto = {
    id: `seeded-${conversations.size}`,
    language: "FR",
    messages: opening(message),
  };
  for (const response of responses) {
    conversation = answered(conversation, response);
  }
  conversations.set(conversation.id, conversation);
  return conversation;
}

export function seedMessages(messages: MessageDto[]): ConversationDto {
  const conversation: ConversationDto = {
    id: `seeded-${conversations.size}`,
    language: "FR",
    messages,
  };
  conversations.set(conversation.id, conversation);
  return conversation;
}

export function answerBehind(conversationId: string, response: string) {
  const conversation = conversations.get(conversationId);
  if (conversation !== undefined) {
    conversations.set(conversationId, answered(conversation, response));
  }
}

function play(pending: ActionMessageDto, response: string): MessageDto[] {
  const step = STEPS[pending.action_id];
  if (step === undefined) {
    throw new Error(`No scripted step for ${pending.action_id}`);
  }
  const { label, messages } = step(pending, response);
  return [
    { role: "USER_ACTION_RESPONSE", action_id: pending.action_id, response, label },
    ...messages,
  ];
}

function answered(conversation: ConversationDto, response: string): ConversationDto {
  const pending = conversation.messages.at(-1);
  if (pending?.role !== "ASSISTANT_ACTION") {
    throw new Error("The conversation has no pending action");
  }
  return { ...conversation, messages: [...conversation.messages, ...play(pending, response)] };
}

export const handlers = [
  http.post(`${API_URL}/conversations`, async ({ request }) => {
    const message = text(await request.json(), "message", MAX_MESSAGE);
    if (message === null || message.length === 0) {
      return invalid("message");
    }
    created += 1;
    const conversation: ConversationDto = {
      id: `conversation-${created}`,
      language: "FR",
      messages: opening(message),
    };
    conversations.set(conversation.id, conversation);
    return HttpResponse.json(conversation, { status: 201 });
  }),

  http.get(`${API_URL}/conversations/:conversationId`, ({ params }) => {
    const conversation = conversations.get(String(params.conversationId));
    return conversation === undefined ? notFound() : HttpResponse.json(conversation);
  }),

  http.post(`${API_URL}/conversations/:conversationId/answers`, async ({ params, request }) => {
    const conversation = conversations.get(String(params.conversationId));
    if (conversation === undefined) {
      return notFound();
    }
    const body: unknown = await request.json();
    const actionId = text(body, "action_id", Number.POSITIVE_INFINITY);
    const response = text(body, "response", MAX_RESPONSE);
    if (actionId === null || response === null) {
      return invalid(actionId === null ? "action_id" : "response");
    }
    const pending = conversation.messages.at(-1);
    if (pending?.role !== "ASSISTANT_ACTION" || pending.action_id !== actionId) {
      return HttpResponse.json({ detail: `ACTION_NOT_FOUND:${actionId}` }, { status: 409 });
    }
    const next = answered(conversation, response);
    conversations.set(next.id, next);
    return HttpResponse.json(next);
  }),
];

export function failing(method: "post" | "get", path: string, { once = true } = {}) {
  return http[method](
    `${API_URL}${path}`,
    () => HttpResponse.json({ detail: "INTERNAL_ERROR" }, { status: 500 }),
    { once },
  );
}
