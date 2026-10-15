const YES = "true";
const NO = "false";

/** @package */
export const ANSWERS = [
  { value: YES, variant: "primary" },
  { value: NO, variant: "signal" },
] as const;

/** @package */
export function yesNoLabel(response: string): string {
  return response === YES ? "Oui" : "Non";
}
