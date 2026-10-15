import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CHOICE, KNOWN_ORDER, QUESTION } from "../api/damagedFlow";
import { renderApp } from "../renderApp";
import {
  answerInComposer,
  describeProblem,
  enabledButton,
  photo,
  photoInput,
  recap,
} from "./steps";

describe("a damaged parcel, from the first message to the end", () => {
  it("guides the client step by step and keeps a recap of every answer", async () => {
    const { user, router } = renderApp();

    await describeProblem(user, "Ma lampe est arrivée cassée");
    expect(await screen.findByText("Ma lampe est arrivée cassée")).toBeDefined();
    await user.click(await enabledButton(CHOICE.damaged.label));
    await waitFor(() => expect(router.state.location.pathname).toMatch(/^\/conversations\//));

    await answerInComposer(user, KNOWN_ORDER);
    await waitFor(() => photoInput());
    await user.upload(photoInput(), photo("lampe.png", "image/png"));
    await user.click(await enabledButton(/envoyer la photo/i));

    expect(await screen.findByText(/pied est fendu/)).toBeDefined();
    await user.click(await enabledButton("Oui"));

    expect(await screen.findByText(/conversation terminée/i)).toBeDefined();
    expect(screen.queryByRole("textbox", { name: /votre réponse/i })).toBeNull();

    const journal = recap();
    expect(journal.getByText(CHOICE.damaged.label)).toBeDefined();
    expect(journal.getByText(KNOWN_ORDER)).toBeDefined();
    expect(journal.getByRole("img")).toBeDefined();
    expect(journal.getByText("Oui")).toBeDefined();
    expect(journal.getByText(/fin de la conversation/i)).toBeDefined();

    await user.click(await enabledButton(/nouvelle demande/i));
    expect(await screen.findByRole("textbox", { name: /expliquez-nous/i })).toBeDefined();
    expect(router.state.location.pathname).toBe("/");
  });

  it("asks again after an invalid order number and keeps one recap row for it", async () => {
    const { user } = renderApp();
    await describeProblem(user, "Colis abîmé");
    await user.click(await enabledButton(CHOICE.damaged.label));

    await answerInComposer(user, "je ne sais plus");
    await answerInComposer(user, KNOWN_ORDER);
    await waitFor(() => photoInput());

    const journal = recap();
    const rows = journal.getAllByRole("button");
    expect(rows).toHaveLength(3);
    expect(journal.getAllByText(QUESTION.order)).toHaveLength(1);
    expect(journal.getByText(KNOWN_ORDER)).toBeDefined();
    expect(journal.queryByText("je ne sais plus")).toBeNull();
  });
});
