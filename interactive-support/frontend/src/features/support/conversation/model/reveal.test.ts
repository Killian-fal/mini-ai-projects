import { describe, expect, it } from "vitest";
import { agent, ask, reply, textInput, user } from "../../../../test/messages";
import { revealCount } from "./reveal";

const messages = [
  user("Bonjour"),
  agent("Votre numéro ?"),
  ask("ORDER", textInput),
  reply("ORDER", "cma_004"),
  agent("Merci."),
];

describe("revealCount", () => {
  it("shows the client's messages that follow without waiting", () => {
    expect(revealCount(messages, 0)).toBe(1);
    expect(revealCount(messages, 3)).toBe(4);
  });

  it("holds the agent's messages back", () => {
    expect(revealCount(messages, 1)).toBe(1);
  });

  it("never goes past the end", () => {
    expect(revealCount(messages, 9)).toBe(5);
  });
});
