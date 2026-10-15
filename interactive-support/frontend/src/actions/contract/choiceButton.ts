import type { CardStatus } from "./types";

type ChoiceButtonProps = { disabled: boolean; "aria-pressed"?: boolean };

export function choiceButtonProps(status: CardStatus, value: string): ChoiceButtonProps {
  return status.state === "pending"
    ? { disabled: false }
    : { disabled: true, "aria-pressed": status.response === value };
}
