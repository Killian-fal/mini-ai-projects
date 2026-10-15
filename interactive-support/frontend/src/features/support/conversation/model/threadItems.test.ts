import { describe, expect, it } from "vitest";
import {
  agent,
  ask,
  end,
  photoUpload,
  reply,
  textInput,
  uniqueChoice,
  user,
} from "../../../../test/messages";
import type { Delivery } from "./delivery";
import { type ThreadItem, threadItems } from "./threadItems";

const idle: Delivery = { outgoing: null, acked: false, failure: null };

const opening = [
  user("Ma lampe est arrivée cassée"),
  agent("Votre demande concerne :"),
  ask("ISSUE", uniqueChoice("Abîmée", "Autre")),
  reply("ISSUE", "CHOICE_0", "Abîmée"),
  agent("C'est noté."),
  agent("Votre numéro de commande ?"),
  ask("ORDER", textInput),
];

const kinds = (items: ThreadItem[]) => items.map((item) => item.kind);

describe("threadItems", () => {
  it("renders a card only for actions answered in a card", () => {
    expect(kinds(threadItems(opening, idle))).toEqual([
      "client",
      "agent",
      "card",
      "client",
      "agent",
      "agent",
    ]);
  });

  it("opens an agent group after the client speaks, not between agent messages", () => {
    const leads = threadItems(opening, idle).flatMap((item) =>
      item.kind === "agent" ? [item.leads] : [],
    );
    expect(leads).toEqual([true, true, false]);
  });

  it("freezes an answered card on its response and shows the answer's label", () => {
    const items = threadItems(opening, idle);
    expect(items[2]).toMatchObject({ status: { state: "answered", response: "CHOICE_0" } });
    expect(items[3]).toMatchObject({ view: { kind: "text", text: "Abîmée" } });
  });

  it("shows the outgoing answer only once acknowledged", () => {
    const messages = [
      ...opening,
      reply("ORDER", "cma_004"),
      agent("Une photo ?"),
      ask("PHOTO", photoUpload),
    ];
    const outgoing = { actionId: "PHOTO", response: "data:image/png;base64,AAAA" };

    const sending = threadItems(messages, { ...idle, outgoing });
    expect(sending.at(-1)).toMatchObject({ kind: "card", status: { state: "sending" } });

    const acked = threadItems(messages, { ...idle, outgoing, acked: true });
    expect(acked.at(-2)).toMatchObject({ kind: "card", status: { state: "answered" } });
    expect(acked.at(-1)).toMatchObject({ kind: "client", anchor: null, view: { kind: "photo" } });
  });

  it("offers a failed card again below the error", () => {
    const failure = { actionId: "ISSUE", response: "CHOICE_1" };
    const items = threadItems(opening.slice(0, 3), { ...idle, failure });
    expect(kinds(items).slice(-4)).toEqual(["card", "unsent", "error", "card"]);
    expect(items[2]).toMatchObject({ status: { state: "failed" } });
    expect(items.at(-1)).toMatchObject({ key: "retry", status: { state: "pending" } });
  });

  it("lets the composer take a failed text answer again", () => {
    const failure = { actionId: "ORDER", response: "cma_004" };
    expect(kinds(threadItems(opening, { ...idle, failure })).slice(-2)).toEqual([
      "unsent",
      "error",
    ]);
  });

  it("closes the thread after the end", () => {
    const messages = [...opening, reply("ORDER", "cma_999"), end("Bonne journée !")];
    expect(kinds(threadItems(messages, idle)).slice(-2)).toEqual(["agent", "ended"]);
  });
});
