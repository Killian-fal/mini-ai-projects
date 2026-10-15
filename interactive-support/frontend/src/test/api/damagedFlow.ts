import type { ActionMessageDto, MessageDto } from "./dto";
import { ask, finish, reask, type Step, say, type Turn } from "./script";

export const ACTION = {
  issue: "OPENING.ISSUE_CHOICE",
  order: "OPENING.ORDER_NUMBER",
  photo: "DAMAGED.PHOTO",
  confirm: "DAMAGED.CONFIRM",
} as const;

export const CHOICE = {
  damaged: { key: "IssueChoice.DAMAGED", label: "Ma commande est arrivée abîmée" },
  other: { key: "IssueChoice.OTHER", label: "Autre chose" },
} as const;

export const QUESTION = {
  issue: "Pour être sûr de bien comprendre, votre demande concerne :",
  order: "Quel est votre numéro de commande ?",
  photo: "Envoyez-nous une photo du produit abîmé.",
  confirm: "Voici ce que je vais transmettre au support. Est-ce correct ?",
} as const;

export const KNOWN_ORDER = "cma_004";

export const SUMMARY = "Commande CMA_004 : lampe de bureau.\nLe pied est fendu.";

const ORDER_NUMBER = /cma_\d+/i;
const PHOTO = /^data:image\/[\w.+-]+;base64,[A-Za-z0-9+/]+={0,2}$/;

export function opening(message: string): MessageDto[] {
  return [
    { role: "USER", text: message },
    say("OpeningCode.ASK_ISSUE_CHOICE", QUESTION.issue),
    ask(ACTION.issue, { type: "UNIQUE_CHOICE", choices: [CHOICE.damaged, CHOICE.other] }),
  ];
}

function chooseIssue(pending: ActionMessageDto, response: string): Turn {
  const { action } = pending;
  const choice =
    action.type === "UNIQUE_CHOICE"
      ? action.choices.find(({ key }) => key === response)
      : undefined;
  if (choice === undefined) {
    return reask(pending, "OpeningCode.INVALID_ISSUE", "Choisissez une des réponses proposées.");
  }
  if (choice.key !== CHOICE.damaged.key) {
    return { label: choice.label, messages: [finish("Merci, bonne journée !")] };
  }
  return {
    label: choice.label,
    messages: [
      say("OpeningCode.VALID_ISSUE", "C'est noté."),
      say("OpeningCode.ASK_ORDER_NUMBER", QUESTION.order),
      ask(ACTION.order, { type: "TEXT_INPUT" }),
    ],
  };
}

function giveOrderNumber(pending: ActionMessageDto, response: string): Turn {
  const number = ORDER_NUMBER.exec(response)?.[0];
  if (number === undefined) {
    return reask(pending, "OpeningCode.INVALID_ORDER_NUMBER", "Je ne trouve pas de numéro.");
  }
  if (number.toLowerCase() !== KNOWN_ORDER) {
    return {
      label: null,
      messages: [
        say("DamagedCode.ORDER_NOT_FOUND", "Je ne trouve aucune commande avec ce numéro."),
        finish("Merci, bonne journée !"),
      ],
    };
  }
  return {
    label: null,
    messages: [
      say("OpeningCode.VALID_ORDER_NUMBER", "Merci, j'ai bien votre numéro de commande."),
      say("DamagedCode.ASK_PHOTO", QUESTION.photo),
      ask(ACTION.photo, { type: "PHOTO_UPLOAD" }),
    ],
  };
}

function sendPhoto(pending: ActionMessageDto, response: string): Turn {
  if (!PHOTO.test(response)) {
    return reask(pending, "PhotoCode.NOT_A_PHOTO", "Ce fichier n'est pas une photo.");
  }
  return {
    label: null,
    messages: [
      { role: "ASSISTANT_GEN", text: QUESTION.confirm },
      ask(ACTION.confirm, { type: "YES_NO", value: SUMMARY, location: null }),
    ],
  };
}

function confirm(pending: ActionMessageDto, response: string): Turn {
  if (response !== "true" && response !== "false") {
    return reask(pending, "DamagedCode.INVALID_CONFIRMATION", "Répondez par oui ou par non.");
  }
  return {
    label: null,
    messages: [
      say("DamagedCode.SENT", "Votre signalement est transmis au support."),
      finish("Merci, bonne journée !"),
    ],
  };
}

export const DAMAGED_STEPS: Record<string, Step> = {
  [ACTION.issue]: chooseIssue,
  [ACTION.order]: giveOrderNumber,
  [ACTION.photo]: sendPhoto,
  [ACTION.confirm]: confirm,
};
