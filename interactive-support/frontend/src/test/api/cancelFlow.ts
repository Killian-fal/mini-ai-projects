import type { ActionMessageDto, MessageDto } from "./dto";
import { ask, finish, reask, type Step, say, type Turn } from "./script";

const ADDRESS_DETAILS = "CANCEL.ADDRESS_DETAILS";
const ADDRESS_CONFIRMATION = "CANCEL.ADDRESS_CONFIRMATION";

export const FOUND = "5 Rue Mercière 69002 Lyon";

export const FIELD = {
  street: { key: "AddressField.STREET", label: "Numéro et rue" },
  postalCode: { key: "AddressField.POSTAL_CODE", label: "Code postal" },
  city: { key: "AddressField.CITY", label: "Ville" },
} as const;

/** The conversation once the agent read the street and the city, the postal code missing. */
export function addressRead(): MessageDto[] {
  return [
    { role: "USER", text: "Je déménage, je voudrais changer l'adresse de ma commande cma_001" },
    say("CancelCode.ASK_NEW_ADDRESS", "Quelle est votre nouvelle adresse de livraison ?"),
    ask("CANCEL.NEW_ADDRESS", { type: "TEXT_INPUT" }),
    {
      role: "USER_ACTION_RESPONSE",
      action_id: "CANCEL.NEW_ADDRESS",
      response: "Au 5 rue Mercière à Lyon",
      label: null,
    },
    say(
      "CancelCode.ASK_ADDRESS_DETAILS",
      "Vérifiez votre nouvelle adresse et complétez-la si besoin.",
    ),
    ask(ADDRESS_DETAILS, {
      type: "FORM",
      fields: [
        { ...FIELD.street, value: "5 rue Mercière" },
        { ...FIELD.postalCode, value: "" },
        { ...FIELD.city, value: "Lyon" },
      ],
    }),
  ];
}

function sentObject(response: string): object | null {
  try {
    const sent: unknown = JSON.parse(response);
    return typeof sent === "object" && sent !== null && !Array.isArray(sent) ? sent : null;
  } catch {
    return null;
  }
}

function fillAddress(pending: ActionMessageDto, response: string): Turn {
  const sent = sentObject(response);
  if (sent === null) {
    return reask(pending, "FormCode.NOT_A_FORM", "Je n'ai pas reçu le formulaire.");
  }
  const fields = pending.action.type === "FORM" ? pending.action.fields : [];
  const filled = fields.every(({ key }) => {
    const value: unknown = Reflect.get(sent, key);
    return typeof value === "string" && value.trim() !== "";
  });
  if (!filled) {
    return reask(pending, "FormCode.MISSING_FIELD", "Remplissez tous les champs.");
  }
  return {
    label: null,
    messages: [
      say("CancelCode.ASK_ADDRESS_CONFIRMATION", "Est-ce bien ici que vous souhaitez être livré ?"),
      ask(ADDRESS_CONFIRMATION, {
        type: "YES_NO",
        value: FOUND,
        location: { latitude: 45.764324, longitude: 4.832535 },
      }),
    ],
  };
}

function confirmAddress(pending: ActionMessageDto, response: string): Turn {
  if (response !== "true") {
    return reask(pending, "ConfirmationCode.NOT_A_BOOLEAN", "Répondez par oui ou par non.");
  }
  return {
    label: null,
    messages: [
      say("CancelCode.ADDRESS_UPDATED", "Votre adresse de livraison est modifiée."),
      finish("Merci, bonne journée !"),
    ],
  };
}

export const CANCEL_STEPS: Record<string, Step> = {
  [ADDRESS_DETAILS]: fillAddress,
  [ADDRESS_CONFIRMATION]: confirmAddress,
};
