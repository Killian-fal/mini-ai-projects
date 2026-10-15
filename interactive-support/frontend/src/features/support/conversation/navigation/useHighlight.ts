import { useEffect, useState } from "react";
import { anchorId } from "./anchor";

const HIGHLIGHT_MS = 1800;

export function useHighlight() {
  const [highlighted, setHighlighted] = useState<readonly number[]>([]);

  useEffect(() => {
    if (highlighted.length === 0) {
      return;
    }
    const timer = setTimeout(() => setHighlighted([]), HIGHLIGHT_MS);
    return () => clearTimeout(timer);
  }, [highlighted]);

  function jump(targets: readonly number[]) {
    const [first] = targets;
    if (first === undefined) {
      return;
    }
    setHighlighted(targets);
    document.getElementById(anchorId(first))?.scrollIntoView({ block: "start" });
  }

  return { highlighted, jump };
}
