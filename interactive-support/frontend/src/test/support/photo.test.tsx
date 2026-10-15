import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CHOICE, KNOWN_ORDER } from "../api/damagedFlow";
import { seedConversation } from "../api/fakeApi";
import { renderApp } from "../renderApp";
import { photo, photoInput } from "./steps";

async function photoRequested() {
  const { id } = seedConversation("Colis abîmé", [CHOICE.damaged.key, KNOWN_ORDER]);
  const app = renderApp(`/conversations/${id}`);
  await waitFor(() => photoInput());
  return app;
}

describe("choosing the photo", () => {
  it("refuses a photo over the size limit before sending it", async () => {
    const { user } = await photoRequested();

    await user.upload(photoInput(), photo("lampe.jpg", "image/jpeg", 8 * 1024 * 1024));

    expect((await screen.findByRole("status")).textContent).toMatch(/lampe\.jpg/);
    expect(screen.getByRole("button", { name: /choisir une autre photo/i })).toBeDefined();
    expect(screen.queryByRole("button", { name: /envoyer la photo/i })).toBeNull();
  });

  it("refuses a file that is not an image", async () => {
    const { user } = await photoRequested();

    await user.upload(photoInput(), photo("facture.pdf", "application/pdf"));

    expect((await screen.findByRole("status")).textContent).toMatch(/facture\.pdf/);
    expect(screen.queryByRole("button", { name: /envoyer la photo/i })).toBeNull();
  });

  it("previews an accepted photo before sending it", async () => {
    const { user } = await photoRequested();

    await user.upload(photoInput(), photo("lampe.webp", "image/webp"));

    expect(await screen.findByRole("img", { name: /aperçu/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /envoyer la photo/i })).toBeDefined();
  });
});
