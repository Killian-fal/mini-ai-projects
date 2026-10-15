import { useEffect, useState } from "react";
import type { Message } from "../../../../api/conversation";
import { isClient, revealCount } from "../model";

const LINK_MS = 650;

export function useReveal(messages: readonly Message[]): number {
  const [shown, setShown] = useState(messages.length);
  const visible = revealCount(messages, shown);
  const total = messages.length;
  const delay = isClient(messages[visible - 1]) ? 0 : LINK_MS;

  useEffect(() => {
    if (visible >= total) {
      return;
    }
    const timer = setTimeout(() => setShown(visible + 1), delay);
    return () => clearTimeout(timer);
  }, [visible, total, delay]);

  return visible;
}
