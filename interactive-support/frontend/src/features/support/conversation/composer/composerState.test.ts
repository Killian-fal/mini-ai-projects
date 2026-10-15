import { describe, expect, it } from "vitest";
import { agent, ask, textInput, user, yesNo } from "../../../../test/messages";
import { type Delivery, exchanges, pendingExchange } from "../model";
import { composerState } from "./composerState";

const idle: Delivery = { outgoing: null, acked: false, failure: null };

const pendingOf = (...messages: Parameters<typeof exchanges>[0]) =>
  pendingExchange(exchanges(messages));

const textPending = pendingOf(user("Bonjour"), agent("Numéro ?"), ask("ORDER", textInput));
const cardPending = pendingOf(user("Bonjour"), agent("Exact ?"), ask("CONFIRM", yesNo("Oui")));

describe("composerState", () => {
  it("opens for an action answered in the composer", () => {
    expect(
      composerState({ ended: false, busy: false, pending: textPending, delivery: idle }),
    ).toEqual({ kind: "active", actionIndex: 2 });
  });

  it("points to the card when a card waits", () => {
    expect(
      composerState({ ended: false, busy: false, pending: cardPending, delivery: idle }),
    ).toEqual({ kind: "locked", reason: "card-pending" });
  });

  it("shows the text being sent, then the agent at work", () => {
    const outgoing = { actionId: "ORDER", response: "cma_004" };
    const input = { ended: false, busy: true, pending: textPending };
    expect(composerState({ ...input, delivery: { ...idle, outgoing } })).toEqual({
      kind: "sending",
      text: "cma_004",
    });
    expect(composerState({ ...input, delivery: { ...idle, outgoing, acked: true } })).toEqual({
      kind: "locked",
      reason: "agent-busy",
    });
  });

  it("locks while a card answer leaves", () => {
    const outgoing = { actionId: "CONFIRM", response: "true" };
    expect(
      composerState({
        ended: false,
        busy: true,
        pending: cardPending,
        delivery: { ...idle, outgoing },
      }),
    ).toEqual({ kind: "locked", reason: "card-sending" });
  });

  it("ends above everything", () => {
    expect(
      composerState({ ended: true, busy: true, pending: textPending, delivery: idle }),
    ).toEqual({
      kind: "ended",
    });
  });
});
