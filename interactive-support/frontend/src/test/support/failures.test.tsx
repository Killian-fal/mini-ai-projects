import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CHOICE } from "../api/damagedFlow";
import { answerBehind, failing, startedConversation } from "../api/fakeApi";
import { renderApp } from "../renderApp";
import { server } from "../server";
import { activeComposer, describeProblem, enabledButton, thread } from "./steps";

describe("when the server fails", () => {
  it("brings the client back to the welcome screen with the message kept", async () => {
    server.use(failing("post", "/conversations"));
    const { user } = renderApp();

    await describeProblem(user, "Ma lampe est cassée");

    const field = await screen.findByRole<HTMLTextAreaElement>("textbox", {
      name: /expliquez-nous/i,
    });
    expect(field.value).toBe("Ma lampe est cassée");
    expect(screen.getByRole("status")).toBeDefined();

    await user.click(await enabledButton(/réessayer/i));
    expect(await enabledButton(CHOICE.damaged.label)).toBeDefined();
  });

  it("marks the answer as not sent and offers the action again", async () => {
    const { user } = renderApp();
    await describeProblem(user, "Ma lampe est cassée");
    const choice = await enabledButton(CHOICE.damaged.label);
    server.use(failing("post", "/conversations/:conversationId/answers"));

    await user.click(choice);

    expect(await screen.findByRole("status")).toBeDefined();
    expect(thread().getAllByText(/non envoyé/i)).toHaveLength(2);
    await user.click(await enabledButton(CHOICE.damaged.label));

    expect(await activeComposer()).toBeDefined();
    expect(screen.queryByRole("status")).toBeNull();
  });

  it("reloads the conversation when the action was already answered elsewhere", async () => {
    const { user } = renderApp();
    await describeProblem(user, "Ma lampe est cassée");
    const choice = await enabledButton(CHOICE.damaged.label);
    answerBehind(startedConversation().id, CHOICE.damaged.key);

    await user.click(choice);

    expect(await activeComposer()).toBeDefined();
    await waitFor(() => expect(thread().getAllByText(CHOICE.damaged.label)).toHaveLength(2));
    expect(screen.queryByRole("status")).toBeNull();
  });
});
