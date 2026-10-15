import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { addressRead, FIELD, FOUND } from "../api/cancelFlow";
import { seedMessages } from "../api/fakeApi";
import { renderApp } from "../renderApp";
import { enabledButton, recap, thread } from "./steps";

const SENT = "5 rue Mercière, 69002, Lyon";

function field(label: string): HTMLInputElement {
  return screen.getByRole<HTMLInputElement>("textbox", { name: label });
}

async function addressFormShown() {
  const { id } = seedMessages(addressRead());
  const app = renderApp(`/conversations/${id}`);
  await enabledButton("Valider");
  return app;
}

describe("checking an address in a form", () => {
  it("shows what the agent read, sends the completed address and confirms it on a map", async () => {
    const { user } = await addressFormShown();
    expect(field(FIELD.street.label).value).toBe("5 rue Mercière");
    expect(field(FIELD.postalCode.label).value).toBe("");
    expect(field(FIELD.city.label).value).toBe("Lyon");

    await user.type(field(FIELD.postalCode.label), "69002");
    await user.click(await enabledButton("Valider"));

    expect(await screen.findByText(FOUND)).toBeDefined();
    expect(screen.getByTitle(/carte de l'adresse/i)).toBeDefined();
    await user.click(await enabledButton("Oui"));

    expect(await screen.findByText(/conversation terminée/i)).toBeDefined();
    expect(thread().getByText(SENT)).toBeDefined();
    expect(recap().getByText(SENT)).toBeDefined();
    expect(field(FIELD.postalCode.label).matches(":disabled")).toBe(true);
    expect(field(FIELD.postalCode.label).value).toBe("69002");
  });

  it("does not send the form while a field is empty", async () => {
    const { user } = await addressFormShown();

    await user.click(await enabledButton("Valider"));

    expect(field(FIELD.postalCode.label).matches(":invalid")).toBe(true);
    expect(screen.getAllByRole("textbox", { name: FIELD.postalCode.label })).toHaveLength(1);
    expect(screen.queryByText(/réponse envoyée/i)).toBeNull();
  });
});
