import { describe, expect, it } from "vitest";
import { agent, ask, end, form, reply, textInput, user, yesNo } from "../../../../test/messages";
import { ending } from "./ending";
import { journalRows } from "./journalRows";

const reasked = [
  user("Colis abîmé"),
  agent("Votre numéro de commande ?"),
  ask("ORDER", textInput),
  reply("ORDER", "abc"),
  agent("Ce n'est pas un numéro valide."),
  ask("ORDER", textInput),
  reply("ORDER", "cma_004"),
  agent("Je résume :"),
  ask("CONFIRM", yesNo("Pied fendu")),
];

describe("journalRows", () => {
  it("keeps one row per action, with its first question and its last answer", () => {
    const [order] = journalRows(reasked);
    expect(order).toEqual({
      actionId: "ORDER",
      question: "Votre numéro de commande ?",
      answer: { kind: "text", text: "cma_004" },
      targets: [1, 3, 6],
    });
  });

  it("leaves the pending action without answer and targets its card", () => {
    expect(journalRows(reasked)[1]).toMatchObject({ answer: null, targets: [7, 8] });
  });

  it("reads a form's answer as its values, in the form's order", () => {
    const [address] = journalRows([
      agent("Vérifiez votre adresse."),
      ask("ADDRESS", form(["Rue", "5 rue Mercière"], ["Ville", ""])),
      reply("ADDRESS", JSON.stringify({ FIELD_1: "Lyon", FIELD_0: "5 rue Mercière" })),
    ]);
    expect(address?.answer).toEqual({ kind: "text", text: "5 rue Mercière, Lyon" });
  });

  it("reads an answer that is not a form as it was sent", () => {
    const [address] = journalRows([
      agent("Vérifiez votre adresse."),
      ask("ADDRESS", form(["Rue", ""])),
      reply("ADDRESS", "5 rue Mercière"),
    ]);
    expect(address?.answer).toEqual({ kind: "text", text: "5 rue Mercière" });
  });
});

describe("ending", () => {
  it("gathers the agent's last words before the end", () => {
    const messages = [
      ...reasked,
      reply("CONFIRM", "true"),
      agent("Merci."),
      agent("C'est transmis."),
      end("Au revoir."),
    ];
    expect(ending(messages)).toEqual({
      text: "Merci. C'est transmis. Au revoir.",
      targets: [messages.length - 1],
    });
  });

  it("is absent while the conversation goes on", () => {
    expect(ending(reasked)).toBeNull();
  });
});
