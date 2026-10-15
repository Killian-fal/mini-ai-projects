import { useEffect, useRef } from "react";

export function useFollowBottom(tail: string) {
  const followed = useRef<string | null>(null);

  useEffect(() => {
    const behavior = followed.current === null ? "instant" : "auto";
    followed.current = tail;
    window.scrollTo({ top: document.documentElement.scrollHeight, behavior });
  }, [tail]);
}
