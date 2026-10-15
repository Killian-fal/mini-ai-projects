import { useEffect, useState } from "react";

const TICK_MS = 250;

export function useElapsed(active: boolean): number {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (!active) {
      return;
    }
    const start = Date.now();
    const timer = setInterval(() => setElapsed(Date.now() - start), TICK_MS);
    return () => {
      clearInterval(timer);
      setElapsed(0);
    };
  }, [active]);

  return elapsed;
}
