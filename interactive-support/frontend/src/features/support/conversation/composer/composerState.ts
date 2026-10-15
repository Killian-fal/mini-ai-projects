import { hasCard } from "../../../../actions";
import type { Delivery, Exchange } from "../model";

export type LockReason = "card-sending" | "agent-busy" | "card-pending";

export type OpenComposerState =
  | { kind: "sending"; text: string }
  | { kind: "locked"; reason: LockReason }
  | { kind: "active"; actionIndex: number };

export type ComposerState = { kind: "ended" } | OpenComposerState;

type ComposerInput = {
  ended: boolean;
  busy: boolean;
  pending: Exchange | null;
  delivery: Delivery;
};

function answersInComposer(pending: Exchange | null): pending is Exchange {
  return pending !== null && !hasCard(pending.action.message.action);
}

export function composerState({ ended, busy, pending, delivery }: ComposerInput): ComposerState {
  if (ended) {
    return { kind: "ended" };
  }
  if (delivery.outgoing !== null && !delivery.acked) {
    return answersInComposer(pending)
      ? { kind: "sending", text: delivery.outgoing.response }
      : { kind: "locked", reason: "card-sending" };
  }
  if (busy) {
    return { kind: "locked", reason: "agent-busy" };
  }
  return answersInComposer(pending)
    ? { kind: "active", actionIndex: pending.action.index }
    : { kind: "locked", reason: "card-pending" };
}
