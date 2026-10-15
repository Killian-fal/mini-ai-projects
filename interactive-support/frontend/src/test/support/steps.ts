import { screen, waitFor, within } from "@testing-library/react";
import type { UserEvent } from "@testing-library/user-event";

export async function describeProblem(user: UserEvent, problem: string) {
  const field = await screen.findByRole("textbox", { name: /expliquez-nous/i });
  await user.type(field, `${problem}{Enter}`);
}

export async function activeComposer(): Promise<HTMLTextAreaElement> {
  const field = await screen.findByRole<HTMLTextAreaElement>("textbox", { name: /votre réponse/i });
  await waitFor(() => {
    if (field.disabled) {
      throw new Error("The composer is still locked");
    }
  });
  return field;
}

export async function answerInComposer(user: UserEvent, text: string) {
  await user.type(await activeComposer(), `${text}{Enter}`);
}

export async function enabledButton(name: string | RegExp): Promise<HTMLButtonElement> {
  return waitFor(() => {
    const button = screen
      .getAllByRole<HTMLButtonElement>("button", { name })
      .find((candidate) => !candidate.disabled);
    if (button === undefined) {
      throw new Error(`No enabled button named ${String(name)}`);
    }
    return button;
  });
}

export function photoInput(): HTMLInputElement {
  const input = document.querySelector<HTMLInputElement>("input[type='file']");
  if (input === null) {
    throw new Error("No photo card is waiting");
  }
  return input;
}

export function photo(name: string, type: string, bytes = 16): File {
  return new File([new Uint8Array(bytes)], name, { type });
}

export function recap() {
  return within(screen.getByRole("region", { name: /questions et réponses/i }));
}

export function thread() {
  return within(screen.getByRole("log"));
}
