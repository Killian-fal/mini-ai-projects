import type { components } from "../schema/schema";

type Schemas = components["schemas"];

export type Conversation = Schemas["ConversationDto"];
export type Language = Conversation["language"];
export type Message = Conversation["messages"][number];
export type Role = Message["role"];
export type MessageOf<R extends Role> = Extract<Message, { role: R }>;
export type ActionMessage = MessageOf<"ASSISTANT_ACTION">;
export type ResponseMessage = MessageOf<"USER_ACTION_RESPONSE">;
export type Action = ActionMessage["action"];
export type ActionType = Action["type"];
export type ActionOf<K extends ActionType> = Extract<Action, { type: K }>;
