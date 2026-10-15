import { type AnswerView, answerView, type CardStatus, hasCard } from "../../../../actions";
import type { Action, Message } from "../../../../api/conversation";
import { cardStatus, type Delivery, targets } from "./delivery";
import { type Exchange, exchanges, pendingExchange } from "./exchanges";
import { isAgent } from "./roles";

export type ThreadItem =
  | { kind: "client"; key: string; anchor: number | null; view: AnswerView }
  | { kind: "unsent"; key: string; view: AnswerView }
  | { kind: "agent"; key: string; anchor: number; text: string; leads: boolean }
  | { kind: "card"; key: string; anchor: number | null; action: Action; status: CardStatus }
  | { kind: "error"; key: string }
  | { kind: "ended"; key: string };

function responseView(exchange: Exchange, response: string, label: string | null): AnswerView {
  return answerView(exchange.action.message.action, response, label);
}

function messageItems(
  message: Message,
  index: number,
  previous: Message | undefined,
  exchangeAt: ReadonlyMap<number, Exchange>,
  delivery: Delivery,
): ThreadItem[] {
  const key = `msg-${index}`;
  const exchange = exchangeAt.get(index);
  switch (message.role) {
    case "USER":
      return [{ kind: "client", key, anchor: index, view: { kind: "text", text: message.text } }];
    case "ASSISTANT":
    case "ASSISTANT_GEN":
      return [{ kind: "agent", key, anchor: index, text: message.text, leads: !isAgent(previous) }];
    case "END":
      return [
        { kind: "agent", key, anchor: index, text: message.text, leads: !isAgent(previous) },
        { kind: "ended", key: "ended" },
      ];
    case "ASSISTANT_ACTION":
      return exchange !== undefined && hasCard(message.action)
        ? [
            {
              kind: "card",
              key,
              anchor: index,
              action: message.action,
              status: cardStatus(exchange, delivery),
            },
          ]
        : [];
    case "USER_ACTION_RESPONSE":
      return exchange === undefined
        ? []
        : [
            {
              kind: "client",
              key,
              anchor: index,
              view: responseView(exchange, message.response, message.label),
            },
          ];
  }
}

function tailItems(pending: Exchange | null, delivery: Delivery): ThreadItem[] {
  if (pending === null) {
    return [];
  }
  const { outgoing, acked, failure } = delivery;
  if (targets(outgoing, pending)) {
    return acked
      ? [
          {
            kind: "client",
            key: "outgoing",
            anchor: null,
            view: responseView(pending, outgoing.response, null),
          },
        ]
      : [];
  }
  if (!targets(failure, pending)) {
    return [];
  }
  const { action } = pending.action.message;
  const retry: ThreadItem[] = hasCard(action)
    ? [{ kind: "card", key: "retry", anchor: null, action, status: { state: "pending" } }]
    : [];
  return [
    { kind: "unsent", key: "unsent", view: responseView(pending, failure.response, null) },
    { kind: "error", key: "error" },
    ...retry,
  ];
}

export function threadItems(messages: readonly Message[], delivery: Delivery): ThreadItem[] {
  const list = exchanges(messages);
  const exchangeAt = new Map<number, Exchange>();
  for (const exchange of list) {
    exchangeAt.set(exchange.action.index, exchange);
    if (exchange.response !== null) {
      exchangeAt.set(exchange.response.index, exchange);
    }
  }
  return [
    ...messages.flatMap((message, index) =>
      messageItems(message, index, messages[index - 1], exchangeAt, delivery),
    ),
    ...tailItems(pendingExchange(list), delivery),
  ];
}
