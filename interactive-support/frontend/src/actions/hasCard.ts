import type { Action } from "../api/conversation";
import { moduleFor } from "./registry";

export function hasCard(action: Action): boolean {
  return moduleFor(action).input.kind === "card";
}
