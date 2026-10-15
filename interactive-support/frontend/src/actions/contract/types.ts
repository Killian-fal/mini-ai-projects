import type { ComponentProps, ComponentType } from "react";
import type { Action, ActionOf, ActionType } from "../../api/conversation";
import type { Card } from "../../ui/Card";

export type CardState = "pending" | "sending" | "answered" | "failed";

export type CardStatus =
  | { state: "pending" }
  | { state: Exclude<CardState, "pending">; response: string };

export type CardProps<A extends Action> = {
  action: A;
  status: CardStatus;
  onAnswer: (response: string) => void;
};

export type AnswerView = { kind: "text"; text: string } | { kind: "photo"; src: string };

export type ActionInput<A extends Action> =
  | {
      kind: "card";
      prompt: string;
      width: ComponentProps<typeof Card>["width"];
      Content: ComponentType<CardProps<A>>;
    }
  | { kind: "composer" };

export type ActionModule<K extends ActionType> = {
  input: ActionInput<ActionOf<K>>;
  answer: (action: ActionOf<K>, response: string, label: string | null) => AnswerView;
};

export type ActionRegistry = { [K in ActionType]: ActionModule<K> };
