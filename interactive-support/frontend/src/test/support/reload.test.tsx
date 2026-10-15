import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CHOICE, KNOWN_ORDER, QUESTION } from "../api/damagedFlow";
import { failing, seedConversation } from "../api/fakeApi";
import { renderApp } from "../renderApp";
import { server } from "../server";
import { enabledButton, thread } from "./steps";

describe("opening a conversation from its address", () => {
  it("shows the whole conversation at once", async () => {
    const { id } = seedConversation("Colis abîmé", [CHOICE.damaged.key, KNOWN_ORDER]);
    renderApp(`/conversations/${id}`);

    expect(await screen.findByRole("log")).toBeDefined();
    expect(thread().getByText(QUESTION.issue)).toBeDefined();
    expect(thread().getByText(QUESTION.photo)).toBeDefined();
    expect(screen.getByRole("button", { name: /choisir une photo/i })).toBeDefined();
  });

  it("explains that an unknown conversation no longer exists", async () => {
    const { user, router } = renderApp("/conversations/expired");

    expect(await screen.findByRole("heading", { level: 1, name: /n’existe plus/i })).toBeDefined();
    await user.click(await enabledButton(/nouvelle demande/i));

    expect(await screen.findByRole("textbox", { name: /expliquez-nous/i })).toBeDefined();
    expect(router.state.location.pathname).toBe("/");
  });

  it("falls back to the error screen when the server keeps failing", async () => {
    const { id } = seedConversation("Colis abîmé", []);
    server.use(failing("get", "/conversations/:conversationId", { once: false }));
    const { user, router } = renderApp(`/conversations/${id}`);

    expect(await screen.findByRole("heading", { level: 1, name: /problème/i })).toBeDefined();
    await user.click(await enabledButton(/nouvelle demande/i));

    expect(await screen.findByRole("textbox", { name: /expliquez-nous/i })).toBeDefined();
    expect(router.state.location.pathname).toBe("/");
  });
});
