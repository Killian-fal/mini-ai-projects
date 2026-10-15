import type { components } from "../../api/schema/schema";

type Schemas = components["schemas"];

export type ConversationDto = Schemas["ConversationDto"];
export type MessageDto = ConversationDto["messages"][number];
export type ActionMessageDto = Schemas["MessageActionDto"];
export type ActionDto = ActionMessageDto["action"];
