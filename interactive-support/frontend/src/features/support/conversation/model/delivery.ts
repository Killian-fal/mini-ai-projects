import type { CardStatus } from "../../../../actions";
import type { Exchange } from "./exchanges";

export type SentAnswer = { actionId: string; response: string };

export type Delivery = {
  outgoing: SentAnswer | null;
  acked: boolean;
  failure: SentAnswer | null;
};

export function targets(answer: SentAnswer | null, exchange: Exchange): answer is SentAnswer {
  return answer !== null && answer.actionId === exchange.action.message.action_id;
}

export function cardStatus(exchange: Exchange, { outgoing, acked, failure }: Delivery): CardStatus {
  if (exchange.response !== null) {
    return { state: "answered", response: exchange.response.message.response };
  }
  if (targets(outgoing, exchange)) {
    return { state: acked ? "answered" : "sending", response: outgoing.response };
  }
  if (targets(failure, exchange)) {
    return { state: "failed", response: failure.response };
  }
  return { state: "pending" };
}
